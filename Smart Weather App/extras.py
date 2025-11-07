import requests
import datetime
import random

def get_today_in_history():
    try:
        # Using a free historical events API
        url = "https://history.muffinlabs.com/date"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            events = data.get("data", {}).get("Events", [])
            if events:
                event = random.choice(events)
                year = event.get("year", "Unknown year")
                description = event.get("text", "")
                return f"📜 On this day in {year}: {description}"
            else:
                return "📜 No historical events available."
        else:
            return "📜 Could not fetch historical events."
    except Exception as e:
        return f"📜 Error fetching history: {e}"

def get_random_fun_fact():
    try:
        response = requests.get("https://uselessfacts.jsph.pl/random.json?language=en")
        if response.status_code == 200:
            return "🤯 " + response.json().get("text", "Fun fact unavailable.")
        else:
            return "Could not load a fun fact."
    except Exception as e:
        return f"Error fetching fun fact: {e}"

def get_daily_quote():
    quotes = [
        "🌟 'The best way to predict the future is to invent it.' – Alan Kay",
        "💭 'Life is 10% what happens to us and 90% how we react to it.' – Charles R. Swindoll",
        "🌱 'Keep your face always toward the sunshine—and shadows will fall behind you.' – Walt Whitman",
        "🔥 'Do not wait for the perfect moment, take the moment and make it perfect.'",
        "🚀 'Believe you can and you're halfway there.' – Theodore Roosevelt"
    ]
    return random.choice(quotes)
