import requests
from config import OPENWEATHER_API_KEY, VISUALCROSSING_API_KEY
from datetime import datetime
import pytz

# ----------- UTILS ------------
def get_coordinates(city):
    try:
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
        response = requests.get(url)
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        return None, None
    except Exception as e:
        print("Geocoding error:", e)
        return None, None


# --------- WEATHER DATA ---------
def get_weather_data(city=None, lat=None, lon=None):
    import requests
    from config import OPENWEATHER_API_KEY

    if lat and lon:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHER_API_KEY}"
    elif city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={OPENWEATHER_API_KEY}"
    else:
        return None

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"].lower(),
            "wind_speed": data["wind"]["speed"]
        }
    return None


# --------- HOURLY FORECAST ---------
def get_hourly_forecast(city):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={VISUALCROSSING_API_KEY}&include=hours&contentType=json"
        response = requests.get(url)
        data = response.json()

        timezone_str = data.get("timezone", "UTC")
        tz = pytz.timezone(timezone_str)
        now = datetime.now(tz)

        today_date = data["days"][0]["datetime"]
        forecast = []

        for hour in data["days"][0]["hours"]:
            hour_time_str = hour["datetime"]
            try:
                full_dt = datetime.strptime(f"{today_date} {hour_time_str}", "%Y-%m-%d %H:%M:%S")
            except ValueError:
                full_dt = datetime.strptime(f"{today_date} {hour_time_str}", "%Y-%m-%d %H:%M")

            full_dt = tz.localize(full_dt)

            if full_dt >= now:
                forecast.append({
                    "time": full_dt.strftime("%H:%M"),
                    "temp": hour["temp"],
                    "icon": hour.get("icon", "clear-day"),
                    "pop": hour.get("precipprob", 0)
                })

            if len(forecast) == 8:
                break

        return forecast

    except Exception as e:
        print("Forecast API error:", e)
        return []


# --------- 5-DAY FORECAST ---------
def get_five_day_forecast(city):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={VISUALCROSSING_API_KEY}&include=days&contentType=json"
        response = requests.get(url)
        data = response.json()

        forecast = []
        for day in data.get("days", [])[:5]:
            forecast.append({
                "date": day["datetime"],
                "min_temp": day["tempmin"],
                "max_temp": day["tempmax"],
                "condition": day.get("conditions", "")
            })

        return forecast

    except Exception as e:
        print("5-Day Forecast API error:", e)
        return []


# --------- TEMPERATURE TREND ---------
def get_temperature_trend(city):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?unitGroup=metric&key={VISUALCROSSING_API_KEY}&include=days&contentType=json"
        response = requests.get(url)
        data = response.json()

        trend = []
        for day in data.get("days", [])[:5]:
            trend.append({
                "date": day["datetime"],
                "avg_temp": (day["tempmin"] + day["tempmax"]) / 2
            })

        return trend

    except Exception as e:
        print("Temperature Trend API error:", e)
        return []


# --------- UV INDEX ---------
def get_uv_index(city):
    try:
        lat, lon = get_coordinates(city)
        if lat is None:
            return None

        url = (
            f"https://api.openweathermap.org/data/2.5/onecall?"
            f"lat={lat}&lon={lon}&exclude=minutely,hourly,daily,alerts&appid={OPENWEATHER_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        return data.get("current", {}).get("uvi")
    except Exception as e:
        print("UV Index error:", e)
        return None


# --------- AIR QUALITY ---------
def get_air_quality(city):
    try:
        lat, lon = get_coordinates(city)
        if lat is None:
            return None

        url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}"
        )
        response = requests.get(url)
        data = response.json()
        aqi = data.get("list", [{}])[0].get("main", {}).get("aqi")

        aqi_description = {
            1: "Good",
            2: "Fair",
            3: "Moderate",
            4: "Poor",
            5: "Very Poor"
        }

        return aqi_description.get(aqi, "Unknown")
    except Exception as e:
        print("Air Quality error:", e)
        return None
