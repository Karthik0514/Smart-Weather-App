import requests
from config import OPENWEATHER_API_KEY

def get_coordinates(city, api_key):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
    res = requests.get(url).json()
    if res:
        return res[0]['lat'], res[0]['lon']
    return None, None

def get_weather_alerts(lat, lon, api_key):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,daily&appid={OPENWEATHER_API_KEY}"
    res = requests.get(url).json()
    return res.get("alerts", [])  
