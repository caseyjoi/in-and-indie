import os
import requests
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def get_trailer_url(game_name):
    params = {
        "part": "snippet",
        "q": f"{game_name} official trailer",
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
    }
    r = requests.get(SEARCH_URL, params=params)
    if r.status_code != 200:
        return None
    items = r.json().get("items", [])
    if not items:
        return None
    video_id = items[0]["id"].get("videoId")
    if not video_id:
        return None
    return f"https://www.youtube.com/watch?v={video_id}"