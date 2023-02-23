import datetime
import requests
import json
import configparser
import pika
import tweepy

config = configparser.ConfigParser()
config.read('config.ini')
bearer_token = config['twitter']['bearer_token']
consumer_key = config['twitter']['api_key']
consumer_key_secret = config['twitter']['api_key_secret']

startDate = datetime.datetime(2022, 10, 1, 0, 0, 0)

def bearer_oauth(r):

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(self):
    sample_rules = [
        {"value":"(PrimeMinister OR #PrimeMinister) place_country:GB", "tag":"Prime Minister"},
        #{"value": "(#London OR London) place_country:GB","tag": "London Tweets"},
        #{"value": "(England OR #England) place_country:GB", "tag": "England"},
        {"value": "(#UKPolitics OR UK Politics) place_country:GB", "tag": "#UKPolitics"},
        {"value": "(UK Politics) place_country:GB", "tag": "UKPolitics"},
        {"value": "(#brexit OR brexit) place_country:GB", "tag": "Brexit"},
        {"value": "(#PoliticalCampaign) place_country:GB", "tag": "#PoliticalCampaign"},
        {"value": "(political campaign) place_country:GB", "tag": "#Political Campaign"},
        {"value": "(#Elected OR Elected) place_country:GB", "tag": "Elected"},
        {"value": "(#Election OR Election) place_country:GB", "tag": "Election"},
        {"value": "(#Leader OR Leader) place_country:GB", "tag": "Leader"},
        {"value": "(#Partisan OR Partisan) place_country:GB", "tag": "Partisan"},
        {"value": "(#NonPartisan OR #Non-Partisan OR non-partisan) place_country:GB", "tag": "Non-Partisan"},
        {"value": "(#Veto OR Veto) place_country:GB", "tag": "Veto"},
        {"value": "(#Referendum OR Referendum) place_country:GB", "tag": "Referendum"},
        {"value": "(#Quorum OR Quorum) place_country:GB", "tag": "Quorum"},
        {"value": "(#Law OR Law) place_country:GB", "tag": "Law"},
        {"value": "(#Candidate OR Candidate) place_country:GB", "tag": "Candidate"},

    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )

    for response_line in response.iter_lines():
        if response_line:
            now = datetime.datetime.now()
            json_response = json.loads(response_line)

#            print(json.dumps(json_response["data"]["text"], indent=4, sort_keys=True))
            print(json.dumps(json_response, indent=4, sort_keys=True))

           connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
           channel = connection.channel()
           channel.queue_declare(queue='TwitterData')
           channel.basic_publish(exchange='', routing_key='TwitterData', body=json.dumps(json_response["data"]["text"]), properties=pika.BasicProperties(delivery_mode = 2))
           connection.close()

            #with open(r'D:\Facultate\Master\An2\Sem1\BigData\TwitterData\TwitterData.csv', 'a', newline='') as file_handle:
                #csv_writer = csv.writer(file_handle)
                #csv_writer.writerow([now.strftime("%Y-%d-%m %H:%M:%S"), json.dumps(json_response["data"]["text"])])

def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)



if __name__ == '__main__':
   main()

