from flask import Flask, render_template
from flask import Response
from flask_cors import CORS, cross_origin
import sqlite3
import json
from datetime import datetime, date, timedelta

app = Flask(__name__)
CORS(app)

def db_connection():
    connection = sqlite3.connect(r'E:\CatiSOA\BackendSOA\SOA\prediction.db')
    return connection

@app.route('/all')
@cross_origin()
def getAll():
    connection = db_connection()
    cur = connection.cursor()
    data = cur.execute('SELECT * FROM prediction_price').fetchall()

    print(type(data))
    for dat in data:
        print(dat)
    connection.close()

    json_list = []
    for item in data:
        dict = {
            "timestamp": item[0],
            "price": item[1]
        }
        json_list.append(dict)

    return Response(json.dumps(json_list), status=200)

@app.route('/yearly')
@cross_origin()
def getByYear():
    current_year = date.today().year
    connection = db_connection()
    cur = connection.cursor()
    data = cur.execute('SELECT * FROM prediction_price').fetchall()

    filteredData = []

    for dat in data:
        dateTime = datetime.strptime(dat[0], '%Y-%m-%d %H:%M:%S.%f').year
        if dateTime == current_year:
            filteredData.append(dat)

    print(filteredData)
    connection.close()

    json_list = []
    for item in filteredData:
        dict = {
            "timestamp": item[0],
            "price": item[1]
        }
        json_list.append(dict)

    return Response(json.dumps(json_list), status=200)

@app.route('/monthly')
@cross_origin()
def getByMonth():

    current_month = date.today().month
    current_year = date.today().year

    connection = db_connection()
    cur = connection.cursor()
    data = cur.execute('SELECT * FROM prediction_price').fetchall()

    filteredData = []

    for dat in data:
        dateTimeMonth = datetime.strptime(dat[0], '%Y-%m-%d %H:%M:%S.%f').month
        dateTimeYear = datetime.strptime(dat[0], '%Y-%m-%d %H:%M:%S.%f').year

        if dateTimeMonth == current_month and dateTimeYear == current_year:
            filteredData.append(dat)
    print(filteredData)
    connection.close()

    json_list = []
    for item in filteredData:
        dict = {
            "timestamp": item[0],
            "price": item[1]
        }
        json_list.append(dict)

    return Response(json.dumps(json_list), status=200)


@app.route('/last_hour')
@cross_origin()
def getLastHour():

    current_time = datetime.utcnow()
    previous_hour = current_time - timedelta(hours=1)

    connection = db_connection()
    cur = connection.cursor()
    data = cur.execute('SELECT * FROM prediction_price').fetchall()
    filteredData = []

    for dat in data:
        entry_timestamp = datetime.strptime(dat[0], '%Y-%m-%d %H:%M:%S.%f')
        if entry_timestamp >= previous_hour:
            filteredData.append(dat)


    print(filteredData)
    connection.close()

    json_list = []
    for item in filteredData:
        dict = {
            "timestamp": item[0],
            "price": item[1]
        }
        json_list.append(dict)

    return Response(json.dumps(json_list), status=200)


@app.route('/last_day')
@cross_origin()
def getLastDay():
    current_time = datetime.utcnow()
    previous_day = current_time - timedelta(days=1)

    connection = db_connection()
    cur = connection.cursor()
    data = cur.execute('SELECT * FROM prediction_price').fetchall()
    filteredData = []

    for dat in data:
        entry_timestamp = datetime.strptime(dat[0], '%Y-%m-%d %H:%M:%S.%f')

        if entry_timestamp >= previous_day:
            filteredData.append(dat)

    print(filteredData)
    connection.close()

    json_list = []
    for item in filteredData:
        dict = {
            "timestamp": item[0],
            "price": item[1]
        }
        json_list.append(dict)

    return Response(json.dumps(json_list), status=200)









@app.route('/')
@cross_origin()
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
