# importing packages
from flask import Flask, render_template, request, jsonify
import json
import requests
from datetime import date, datetime 
import os
from os.path import join, dirname
from dotenv import load_dotenv

# app instantiation
app = Flask(__name__)

# environment variable
load_dotenv(verbose=True)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
api_key = os.environ.get("API_KEY")

# prefecture data
prefectures = ["Hokkaido", "Akita", "Aomori", "Fukushima", "Iwate", "Miyagi", "Yamagata", "Chiba", "Gunma", "Ibaraki", "Kanagawa", "Saitama", "Tochigi", "Tokyo", "Aichi", "Fukui", "Gifu", "Ishikawa", "Nagano", "Niigata", "Shizuoka", "Toyama", "Yamanashi", "Hyogo", "Kyoto", "Mie", "Nara", "Osaka", "Shiga", "Wakayama", "Hiroshima", "Okayama", "Shimane", "Tottori", "Yamaguchi", "Ehime", "Kagawa", "Kochi", "Tokushima", "Fukuoka", "Kagoshima", "Kumamoto", "Miyazaki", "Nagasaki", "Oita", "Okinawa", "Saga"]

# root route
@app.route("/", methods=["GET"])
def home():
  # get current location with client ip
  client_ip = jsonify({"ip": request.remote_addr})
  request_url = f"https://geolocation-db.com/jsonp/{client_ip}"
  response_data = requests.get(request_url).content.decode().split("(")[1].strip(")")
  location = json.loads(response_data).get("state")

  # get weather info by city name
  get_current_weather = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric")
  data = get_current_weather.json()
  
  # weather data of current location
  current_weather = {
    "date": date.today(),
    "time": datetime.now().strftime("%H"),
    "location": location,
    "temp": int(data.get("main").get("temp")),
    "description": data.get("weather")[0].get("description"),
    "icon": data.get("weather")[0].get("icon")[0:2]
  }

  # get next 7days forecast (lat, lang)
  # API call
  lat = data.get("coord").get("lat")
  lon = data.get("coord").get("lon")
  get_forecast = requests.get(f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly&appid={api_key}&units=metric")
  data = get_forecast.json()
  # function for mapping the necessary info
  def make_forcast(obj):
    return {
      "date": date.fromtimestamp(obj.get("dt")),
      "temp": int(obj.get("temp").get("day")),
      "description": obj.get("weather")[0].get("description"),
      "icon": obj.get("weather")[0].get("icon")[0:2]
    }
  # data manipulation with map
  weather_forecast = list(map(make_forcast, data.get("daily")))


  return render_template("index.html", current_weather=current_weather, weather_forecast=weather_forecast)

# route for regions
@app.route("/regions", methods=["POST", "GET"])
def regions():
  if request.method == "POST":
    # assign a variable for selected prefecture
    prefecture = request.form["prefecture"]

    # make api call based on the selected prefecture
    get_pref_weather = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={prefecture}&appid={api_key}&units=metric")
    data = get_pref_weather.json()

    # weather data of selected prefecture
    pref_weather = {
    "date": date.today(),
    "time": datetime.now().strftime("%H"),
    "location": prefecture,
    "temp": int(data.get("main").get("temp")),
    "temp_max": int(data.get("main").get("temp_max")),
    "temp_min": int(data.get("main").get("temp_min")),
    "humidity": data.get("main").get("humidity"),
    "wind": data.get("wind").get("speed"),
    "description": data.get("weather")[0].get("description"),
    "icon": data.get("weather")[0].get("icon")[0:2]
    }

    print(pref_weather, type(pref_weather))
    return render_template("regions.html", prefectures=prefectures, pref_weather=pref_weather)
  else:
    return render_template("regions.html", prefectures=prefectures, pref_weather="Please select a prefecture")


# server setup
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))