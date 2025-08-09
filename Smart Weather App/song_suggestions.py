import requests
import random
from config import LASTFM_API_KEY  # Your API key goes here

# Weather condition to tag mapping
weather_tag_map = {
    "rain": "rain",
    "clear": "happy",
    "sun": "sun",
    "cloud": "chill",
    "snow": "calm",
    "storm": "dark",
    "fog": "ambient",
    "drizzle": "acoustic"
}

def get_daily_song(condition: str) -> str:
    condition = condition.lower()

    for keyword, tag in weather_tag_map.items():
        if keyword in condition:
            return get_random_song_by_tag(tag)

    return get_random_song_by_tag("chill")  # Fallback

def get_random_song_by_tag(tag: str) -> str:
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "tag.gettoptracks",
        "tag": tag,
        "api_key": LASTFM_API_KEY,
        "format": "json",
        "limit": 30  # Fetch more songs to randomize
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        tracks = data.get("tracks", {}).get("track", [])
        if not tracks:
            return "🎵 No track found for this weather."

        song = random.choice(tracks)
        name = song.get("name")
        artist = song.get("artist", {}).get("name")
        return f"🎶 {name} by {artist}"


    except Exception as e:
        print("Last.fm error:", e)
        return "⚠️ Could not fetch song from Last.fm."
