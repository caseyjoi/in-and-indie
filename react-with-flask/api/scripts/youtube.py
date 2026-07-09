import os
import requests
from dotenv import load_dotenv

load_dotenv()
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"

def get_trailer_url(game_name):
    params = {
        "part": "snippet",
        "q": f"{game_name} game trailer", # Relaxed strictness to catch more Indie trailers
        "type": "video",
        "maxResults": 1,
        "key": YOUTUBE_API_KEY,
    }
    r = requests.get(SEARCH_URL, params=params)
    
    """
    # Debugger:
    if r.status_code != 200:
        print(f"\n[YOUTUBE API ERROR for '{game_name}'] - Status {r.status_code}")
        #print(r.text) # This will tell you if you hit the 10,000 unit daily quota.
        return None
    """
        
    items = r.json().get("items", [])
    if not items:
        print(f"[YOUTUBE] No trailer found for '{game_name}'")
        return None
        
    video_id = items[0]["id"].get("videoId")
    if not video_id:
        return None
        
    return f"https://www.youtube.com/watch?v={video_id}"