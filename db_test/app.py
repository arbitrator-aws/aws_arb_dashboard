from chalice import Chalice, Response
import json
import datetime as dt
import jinja2
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import math

app = Chalice(app_name='db_test')

@app.route('/', cors=True)
def index():
    local = False
    curr_ts = dt.datetime.now()
    if local:
        # local
        curr_rate = 16.3
        padded_rate = curr_rate + 0.44
        curr_kraken_euro = 9500
        curr_kraken_zar = curr_kraken_euro * padded_rate
        curr_luno = 165000
        # local
        with open("chalicelib/static/data/data2.json", "r") as f:
            data = json.load(f)
        series = data["data"]["series"]
        # print(series)
    else:
        # Remote
        ddb_resource = boto3.resource('dynamodb')
        # define tables
        tbl_btc = ddb_resource.Table('arbitrator-btc-hist-minutely')
        tbl_forex = ddb_resource.Table('arbitrator-forex-hist-halfhourly')
        tbl_agg = ddb_resource.Table('arbitrator-aggregations')
        # Query FS to get current point values
        # # Forex rate
        forex_timestamp = int(curr_ts.replace(minute = math.floor(curr_ts.minute/30.0) * 30, second=0, microsecond=0).timestamp())
        curr_rate = float(tbl_forex.query(
            KeyConditionExpression=Key('source').eq("fixer") & Key('timestamp_utc').eq(forex_timestamp),
            ProjectionExpression='content.rates.ZAR'
            )["Items"][0]["content"]["rates"]["ZAR"])
        padded_rate = curr_rate + 0.44
        # curr_ts = rates["timestamp"]

        # Pull BTC prices from 2 min ago
        btc_timestamp = int(curr_ts.replace(minute = (curr_ts.minute-2), second=0, microsecond=0).timestamp())
        # kraken
        curr_kraken_euro = float(tbl_btc.query(
            KeyConditionExpression=Key('exchange').eq("kraken") & Key('timestamp_utc').eq(btc_timestamp),
            ProjectionExpression='content.result_price_last'
            )["Items"][0]["content"]["result_price_last"])

        curr_kraken_zar = curr_kraken_euro * padded_rate
        # Luno
        # q_fs_luno = fs_client.collection(u'luno').order_by(u'timestamp', direction=firestore.Query.DESCENDING).limit(1).get()
        curr_luno = float(tbl_btc.query(
            KeyConditionExpression=Key('exchange').eq("luno") & Key('timestamp_utc').eq(btc_timestamp),
            ProjectionExpression='content.result_price_last'
            )["Items"][0]["content"]["result_price_last"])

        # Query the hourly cache data:
        # Remote
        agg_timestamp = int(curr_ts.replace(minute = 0, second=0, microsecond=0).timestamp())
        series = (tbl_agg.query(
            KeyConditionExpression=Key('range').eq("hourly") & Key('timestamp_utc').eq(agg_timestamp),
            ProjectionExpression='series'
            )["Items"])
            import pprint
        pprint.pprint(series[0]["series"])
        # q_fs = fs_client.collection(u'cache').order_by(u'timestamp_ms', direction=firestore.Query.DESCENDING).limit(1).get()
        # series = {"data": {key:doc.to_dict()[key] for key in doc.to_dict().keys()} for doc in q_fs}["data"]["series"]
    return series


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
