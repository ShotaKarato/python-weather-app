# importing packages
from flask import Flask, render_template
import requests
from datetime import date 
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
prefectures = {
  "Hokkaido": ["Hokkaido"],
  "Tohoku": ["Akita", "Aomori", "Fukushima", "Iwate", "Miyagi", "Yamagata"],
  "Kanto": ["Chiba", "Gunma", "Ibaraki", "Kanagawa", "Saitama", "Tochigi", "Tokyo"],
  "Chubu": ["Aichi", "Fukui", "Gifu", "Ishikawa", "Nagano", "Niigata", "Shizuoka", "Toyama", "Yamanashi"],
  "Kansai": ["Hyogo", "Kyoto", "Mie", "Nara", "Osaka", "Shiga", "Wakayama"],
  "Chugoku": ["Hiroshima", "Okayama", "Shimane", "Tottori", "Yamaguchi"],
  "Shikoku": ["Ehime", "Kagawa", "Kochi", "Tokushima"],
  "Kyushu & Okinawa": ["Fukuoka", "Kagoshima", "Kumamoto", "Miyazaki", "Nagasaki", "Oita", "Okinawa", "Saga"]
}

# root route
@app.route("/")
def home():
  # get current location (city name)
  geo_request_url = 'https://get.geojs.io/v1/ip/geo.json'
  geo_data = requests.get(geo_request_url).json()
  location = geo_data['city']

  # get weather info by city name
  get_current_weather = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric")
  data = get_current_weather.json()
  
  # weather data of current location
  current_weather = {
    "date": date.today(),
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

@app.route("/regions")
def regions():
  return render_template("index.html")

# server setup
if __name__ == "__main__":
  app.run(debug=True)