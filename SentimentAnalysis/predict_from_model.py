import flask
import numpy
import pickle
import argparse

import numpy as np

from tensorflow import keras
from tensorflow.keras.preprocessing.sequence import pad_sequences

CLASS_MAPPING = {
    "0": "negative",
    "2": "neutral",
    "4": "positive"
}

tokenizer = None
model = None
maxlen = None

app = flask.Flask(__name__)


def load_model(path):
    global model
    model = keras.models.load_model(
                r"{}".format(path))


def load_tokenizer(path):
    global tokenizer
    with open(path, 'rb') as handle:
        tokenizer = pickle.load(handle)


def load_maxlen(path):
    global maxlen
    with open(path, "r") as handle:
        maxlen = int(handle.read())


def load_all_same_path(path):
    load_model(path + "\\model.tfsm")
    load_tokenizer(path + "\\tokenizer.pickle")
    load_maxlen(path + "\\data_shape.txt")

def prepare_input(input_data, tokenizer, maxlen):
    if not isinstance(input_data, list):
        input_data = [input_data]

    new_data = numpy.asarray(input_data)
    seq_pred = tokenizer.texts_to_sequences(new_data)
    d_pred = pad_sequences(seq_pred, maxlen=maxlen)

    return d_pred


@app.route("/predict", methods=["POST"])
def predict():
    data = {"success": False}

    if flask.request.method == "POST":

        try:
            user_input = flask.request.json
            print(user_input)
            data['predictions'] = []

            global tokenizer, maxlen, model
            processed = prepare_input(user_input.get('data'), tokenizer, maxlen)

            predictions = model.predict(processed)
            transformed_predictions = [CLASS_MAPPING[str(np.argmax(x))] for x in predictions.tolist()]
            data['predictions'] = transformed_predictions
            data['success'] = True
        except Exception as exc:
            print(exc)

    return flask.jsonify(data)


def get_parser():
    parser = argparse.ArgumentParser(prog='Prediction server')

    subparsers = parser.add_subparsers(dest='parser_type')

    parser_separate = subparsers.add_parser("separate_paths")
    parser_separate.add_argument('-mp', '--model_path')
    parser_separate.add_argument('-tp', '--tokenizer_path')
    parser_separate.add_argument('-pp', '--padding_path')

    parser_same = subparsers.add_parser("same_path")
    parser_same.add_argument('-p', '--path')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    print(args)

    print("Loading model...")
    if args.parser_type == "separate_paths":
        load_model(args.model_path)
        load_tokenizer(args.tokenizer_path)
        load_maxlen(args.padding_path)
    elif args.parser_type == "same_path":
        load_all_same_path(args.path)

    app.run(host="0.0.0.0")
