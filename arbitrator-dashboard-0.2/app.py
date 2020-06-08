from chalice import Chalice, Response
import json
import datetime as dt
import jinja2
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr
import math


app = Chalice(app_name="arbitrator-dashboard-0-2")

@app.route("/", cors=False)
def index():
    local = False
    curr_ts = dt.datetime.now(dt.timezone.utc)
    # BTC timestamp 2 min ago
    btc_timestamp = int((curr_ts.replace(second=0, microsecond=0) - dt.timedelta(minutes=2)).timestamp())
    # forex timestamp, round down to 30 min mark
    # forex_timestamp = int(curr_ts.replace(minute = math.floor(curr_ts.minute/30.0) * 30, second=0, microsecond=0).timestamp())
    forex_timestamp = int(curr_ts.replace(minute = 0, second=0, microsecond=0).timestamp())
    # aggregates timestamp - previous hour mark
    agg_timestamp = int(curr_ts.replace(minute = 0, second=0, microsecond=0).timestamp())

    rate_padding = 0.29

    if local:
        # local
        curr_rate = 16.3
        padded_rate = curr_rate + rate_padding
        curr_kraken_euro = 9500
        curr_kraken_zar = curr_kraken_euro * padded_rate
        curr_luno = 165000
        # local
        with open("chalicelib/static/data/data3.json", "r") as f:
            data = json.load(f)
        series = data["data"]["series"]
    else:
        # Remote
        ddb_resource = boto3.resource("dynamodb")

        # define tables
        tbl_btc = ddb_resource.Table("arbitrator-btc-hist-minutely")
        tbl_forex = ddb_resource.Table("arbitrator-forex-hist-halfhourly")
        tbl_agg = ddb_resource.Table("arbitrator-aggregations")

        # Forex rate from closest 30 min mark
        curr_rate = float(tbl_forex.query(
            KeyConditionExpression=Key("source").eq("fixer") & Key("timestamp_utc").eq(forex_timestamp),
            ProjectionExpression="content.rates.ZAR"
            )["Items"][0]["content"]["rates"]["ZAR"])
        padded_rate = curr_rate + rate_padding

        # Pull BTC prices from 2 min ago
        # kraken
        curr_kraken_euro = float(tbl_btc.query(
            KeyConditionExpression=Key("exchange").eq("kraken") & Key("timestamp_utc").eq(btc_timestamp),
            ProjectionExpression="content.result_price_last"
            )["Items"][0]["content"]["result_price_last"])

        curr_kraken_zar = curr_kraken_euro * padded_rate
        # Luno
        curr_luno = float(tbl_btc.query(
            KeyConditionExpression=Key("exchange").eq("luno") & Key("timestamp_utc").eq(btc_timestamp),
            ProjectionExpression="content.result_price_last"
            )["Items"][0]["content"]["result_price_last"])

        # Query the hourly cache data:
        series = (tbl_agg.query(
            KeyConditionExpression=Key("range").eq("hourly") & Key("timestamp_utc").eq(agg_timestamp),
            ProjectionExpression="series"
            )["Items"][0]["series"])

        

        # get rid of those decimals
        series = [
            { 
            "datetime_max": d["datetime_max"], 
            "timestamp_ms": int(d["timestamp_ms"]),
            "arb":float(d["arb"]), 
            "arb_min":float(d["arb_min"]), 
            "arb_max":float(d["arb_max"]),
            "kraken": float(d["kraken"]), 
            "kraken_min": float(d["kraken_min"]), 
            "kraken_max": float(d["kraken_max"]), 
            "luno": float(d["luno"]), 
            "luno_min": float(d["luno_min"]), 
            "luno_max": float(d["luno_max"]), 
            "rate": float(d["rate"])
            } for d in series]


        
    curr_data = {"ts":str(curr_ts.replace(microsecond=0)), 
        "luno":round(curr_luno,2), 
        "krakene":round(curr_kraken_euro,2), 
        "krakenz":round(curr_kraken_zar,2), 
        "arb":round(((curr_luno-curr_kraken_zar)/curr_kraken_zar)*100, 2), 
        "rate":round(curr_rate, 2), 
        "rate_padding":rate_padding,
        "rate_padded":round(padded_rate, 2)  
        }

    # Load the local files for html injection - this breaks with CORS on GCP if you do it in html
    # main css
    file_dashboard_css = open("chalicelib/static/css/dashboard.css","r") 
    dashboard_css = file_dashboard_css.read()

    file_form_calcs_js = open("chalicelib/static/js/form_calcs.js","r") 
    form_calcs_js = file_form_calcs_js.read()

    file_charts_js = open("chalicelib/static/js/charts.js","r")  
    charts_js = file_charts_js.read()

    # Conform data for highcharts
    #----------------------------
    # Hourly prices line chart
    h_prices_id = "h_prices_id"
    h_prices_chart = {"type": "spline", "height": 350}
    h_prices_data = [{"name":"Kraken", "data":[[series[i]["timestamp_ms"], series[i]["kraken"]] for i in range(len(series))]},
                     {"name":"Luno", "data":[[series[i]["timestamp_ms"], series[i]["luno"]] for i in range(len(series))]}]
    h_prices_title = {"text": "Hourly BTC price"}
    h_prices_xAxis = {"type": "datetime"}
    h_prices_yAxis = {"title": {"text": "BTC Price (ZAR)"}, "lineWidth": 1}
    h_prices_params = {"h_prices_idv":h_prices_id, "h_prices_chart":h_prices_chart, "h_prices_data":h_prices_data, "h_prices_title":h_prices_title, 
                       "h_prices_xAxis":h_prices_xAxis, "h_prices_yAxis":h_prices_yAxis}


    # Hourly Arbitrage chart
    h_arb_id = "h_arb_id"
    h_arb_chart = {"type": "spline", "height": 350}
    
    h_arb_series = [[series[i]["timestamp_ms"], series[i]["arb"]] for i in range(len(series))]
    h_arb_data = [{"name":"Arbitrage", "data":h_arb_series}]

    h_arb_new_data = [series[i]["arb"] for i in range(len(series))]
    h_arb_new_start = min([series[0]["timestamp_ms"] for i in range(len(series))])
    h_arb_new_int = 3600 * 1000

    h_arb_title = {"text": "Hourly Arbitrage (Uncorrected rate, no fees)"}
    h_arb_xAxis = {"type": "datetime"}
    h_arb_yAxis = {"title": {"text": "Arbitrage (%)"}, "lineWidth": 1}
    h_arb_params = {
        "h_arb_idv":h_arb_id, 
        "h_arb_chart":h_arb_chart, 
        "h_arb_data":h_arb_data, 
        "h_arb_title":h_arb_title, 
        "h_arb_xAxis":h_arb_xAxis, 
        "h_arb_yAxis":h_arb_yAxis,
        "h_arb_new_data":h_arb_new_data, 
        "h_arb_new_start":h_arb_new_start,
        "h_arb_new_int":h_arb_new_int}



    # # CORS stuff: https://cloud.google.com/functions/docs/writing/http
    # # Set CORS headers for the preflight request
    # if request.method == "OPTIONS":
    #     # Allows GET requests from any origin with the Content-Type
    #     # header and caches preflight response for an 3600s
    #     headers = {
    #         # "X-Content-Type-Options": "text/html",
    #         "Access-Control-Allow-Origin": "*",
    #         "Access-Control-Allow-Methods": "GET",
    #         "Access-Control-Allow-Headers": "Content-Type",
    #         "Access-Control-Max-Age": "3600"
    #     }
    #     return ("", 204, headers)

    # Set CORS headers for the main request
    cust_headers = {
        "Content-Type": "text/html",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "*"
    }

    # Page rendering
    context = {
        "form_calcs_js": form_calcs_js,
        "dashboard_css":dashboard_css, 
        "charts_js":charts_js, 
        "msg":"hello", 
        **curr_data, 
        **h_prices_params, 
        **h_arb_params}

    def render(tpl_path, context):
        path, filename = os.path.split(tpl_path)
        return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")).get_template(filename).render(context)

    resp = render("chalicelib/templates/dashboard.html", context)

    return Response(body=resp,
                    status_code=200,
                    headers=cust_headers)