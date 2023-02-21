import requests
import datetime as dt
import json
from flask import Flask, jsonify, request
#here your api token
API_TOKEN = ""
#put here your api key
RSA_API_KEY = ""
app = Flask(__name__)

def correct_request(querystring_start):
    querystring = {"startDateTime": querystring_start["date"]+"T00:00:00",
               "aggregateHours":"24",
               "location": querystring_start["location"],
               "endDateTime":querystring_start["date"]+"T18:59:59",
               "unitGroup":"metric",
               "contentType":"json",
              }
    return querystring
def generate_stuff(querystring):
    

    url = "https://visual-crossing-weather.p.rapidapi.com/history"

    headers = {
        "X-RapidAPI-Key": RSA_API_KEY,
        "X-RapidAPI-Host": "visual-crossing-weather.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    return response.json()

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def get_weather_text(response_data, querystring):
    weather_data_now = {
        "temp_c": response_data["locations"][querystring["location"]]["values"][0]["temp"],
        "wind_kph": response_data["locations"][querystring["location"]]["values"][0]["wspd"],
        "pressure_mb": response_data["locations"][querystring["location"]]["values"][0]["sealevelpressure"],
        "humidity": response_data["locations"][querystring["location"]]["values"][0]["humidity"],
        "temp_max": response_data["locations"][querystring["location"]]["values"][0]["maxt"],
        "temp_min": response_data["locations"][querystring["location"]]["values"][0]["mint"],
        "visibility": response_data["locations"][querystring["location"]]["values"][0]["visibility"],
        "conditions": response_data["locations"][querystring["location"]]["values"][0]["conditions"],
    }
    return weather_data_now


@app.route("/")
def home_page():
    return "<p><h2>Homework SaaS. SK.</h2></p>"

@app.route(
    "/homeworkSaaS/check",
    methods=["POST"],
)


def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)
        
        
        
    querystring_start = json_data
    querystring = correct_request(querystring_start)
    response_data = generate_stuff(querystring)
    
    
    weather = get_weather_text(response_data,querystring)
    time_now = dt.datetime.now()

    result = {
        "requester_name": querystring_start["requester_name"],
        "timastamp": time_now.isoformat(),
        "location": querystring["location"],
        "date": querystring_start["date"],
        "weather": weather
    }
        

    return result
