import datetime
import json
import sys
import uuid

import pika
import redis
import logging
import requests
import sqlite3


import configparser
cfg = configparser.ConfigParser()
cfg.read("./config_file.ini")

CLASSIFIER_HOST = cfg.get("hosts", "classifier", fallback="172.17.0.2")
RABBITMQ_HOST = cfg.get("hosts", "rabbitmq", fallback="172.17.0.3")
REDIS_HOST = cfg.get("hosts", "redis", fallback="172.17.0.4")

QUEUE_NAME = cfg.get("misc", "queue_name")

LOG_PATH = "./logs"
FILE_NAME = "core-app"

redis_client = redis.Redis(host=REDIS_HOST)
database = sqlite3.connect("prediction.db")

class SentimentClassification(object):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


def setup_logger():
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
    root_logger = logging.getLogger()

    file_handler = logging.FileHandler("{0}/{1}.log".format(LOG_PATH, FILE_NAME))
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

    return root_logger


_LOGGER_ = setup_logger()


def create_rabbitmq_channel(queue=None):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    return channel


def classify_tweet(text):
    response = requests.post(CLASSIFIER_HOST, json={"data": text})
    if not response.status_code == 200:
        _LOGGER_.error("Classification server has encountered an error.")
    json_response = response.json()
    if json_response['success'] == "false":
        _LOGGER_.error("Classification server has encountered an error.")
    return json_response['predictions'][0]


def parse_input(data):
    return 0, data
    # TODO: nush
    timestamp = data[0]
    body = data[1]
    return timestamp, body

def get_start_of_next_week_timestamp(reference_timestamp):
    start_of_next_week = (reference_timestamp -
                          datetime.timedelta(days=reference_timestamp.weekday())).replace(hour=0,
                                                                                          minute=0,
                                                                                          second=0,
                                                                                          microsecond=0) \
                         + datetime.timedelta(days=7)
    return start_of_next_week


def increment_redis_key(key_name, expiration_value=None):
    redis_key = redis_client.get(key_name)
    if not redis_key:
        redis_client.set(key_name, 0, int(expiration_value))
    redis_client.incr(key_name, 1)

def ingest_tweets(channel, method, properties, body):
    input_id = uuid.uuid4()
    try:
        _LOGGER_.info(" [x] Ingested input with id {}, data: {}".format(input_id, body))
        timestamp, tweet = parse_input(body)
        tweet = tweet.decode('utf-8')
        sentiment = classify_tweet(tweet)
        _LOGGER_.info("Tweet {} was classified as: {}".format(input_id, sentiment))

        # count sentiment of tweets in this week
        current_timestamp = datetime.datetime.now()
        start_of_next_week = get_start_of_next_week_timestamp(current_timestamp)
        sentiment_expiration = (start_of_next_week - current_timestamp).total_seconds()

        if sentiment != SentimentClassification.NEUTRAL:
            increment_redis_key("total", sentiment_expiration)
        increment_redis_key(sentiment, sentiment_expiration)

        # compute how much will the price change next week
        procent_cost = float(redis_client.get("procent_cost"))
        last_positives_ratio = float(redis_client.get("positives_ratio"))
        last_average = float(redis_client.get('average'))
        _LOGGER_.info("Baseline data: cost_of_percent: {}; positives_ration: {}; average: {}".format(procent_cost, last_positives_ratio, last_average))

        average_change = last_average

        total_tweets = int(redis_client.get("total"))
        if total_tweets != 0:
            total_positives = redis_client.get(SentimentClassification.POSITIVE)
            if not total_positives:
                total_positives = 0
            current_positives_ratio = (total_positives/total_tweets)*100
            _LOGGER_.info("Current ratio of positives to negatives: {}".format(current_positives_ratio))

            percent_deviation = last_positives_ratio - current_positives_ratio
            _LOGGER_.info("Percentage deviation from baseline: {}".format(percent_deviation))
            cost_change = percent_deviation * procent_cost
            _LOGGER_.info("Change of cost from baseline average: {}".format(cost_change))
            average_change = last_average + cost_change
            _LOGGER_.info("New predicted price: {}".format(average_change))

        # write new prediction for Tableau
        with open("./realtime_prediction.csv", "a+") as fout:
            fout.write("{},{}\n".format(current_timestamp, average_change))

        # write to hive
        with open("./tweets.csv", "a+") as fout:
            fout.write("{},{},'{}',{}\n".format(input_id, timestamp, tweet, sentiment))

        cursor_object = database.cursor()
        query = "UPDATE trust_search SET processed = ?, trust_percentage = ? WHERE trust_search.search_id = ?"
        values = (True, positive_ratio, request_identifier)

        cursor_object.execute(query, values)
        database.commit()


        _LOGGER_.info("Successfully processed id {}".format(input_id))
    except Exception as exc:
        _LOGGER_.exception("Something unexpected happened when processing id {}".format(input_id))


connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
channel = connection.channel()
channel.queue_declare(queue="testda")
channel.basic_consume(queue="testda",
                      auto_ack=True,
                      on_message_callback=ingest_tweets)
channel.start_consuming()
