import requests

def get_user_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        if response.status_code == 200:
            data = response.json()
            return data.get("city", "Unknown")
    except Exception as e:
        print("Auto-location error:", e)
    return None
