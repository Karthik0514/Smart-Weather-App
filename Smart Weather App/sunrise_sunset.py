import requests
from config import VISUALCROSSING_API_KEY

def get_sunrise_sunset(city):
    try:
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city}?key={VISUALCROSSING_API_KEY}&include=days&elements=sunrise,sunset"
        response = requests.get(url)
        data = response.json()

        if "days" not in data or not data["days"]:
            return "⚠️ Sunrise and sunset data not available."

        today = data["days"][0]
        sunrise = today.get("sunrise", "N/A")
        sunset = today.get("sunset", "N/A")

        return f"🌅 **Sunrise:** {sunrise}\n🌇 **Sunset:** {sunset}"

    except Exception as e:
        print("Error fetching sunrise/sunset:", e)
        return "⚠️ Could not retrieve sunrise/sunset times."
