"""
Get users top 5 played games from steam. Afterwards, compile the tags from those games.
"""

import os
import requests
from dotenv import load_dotenv
load_dotenv()

# Maps Steam tags to IGDB IDs and their category.
STEAM_TO_IGDB_MAP = {
    "Action": {"id": 1, "type": "themes"},
    "RPG": {"id": 12, "type": "genres"},
    "JRPG": {"id": 12, "type": "genres"}, # Maps to general RPG
    "Sci-fi": {"id": 18, "type": "themes"},
    "Adventure": {"id": 31, "type": "genres"},
    "Story Rich": {"id": 31, "type": "genres"}, # Maps to Adventure
    "Horror": {"id": 19, "type": "themes"},
    "Survival Horror": {"id": 19, "type": "themes"},
    "Simulation": {"id": 13, "type": "genres"},
    "Strategy": {"id": 15, "type": "genres"},
    "Open World": {"id": 38, "type": "themes"},
    "Fantasy": {"id": 17, "type": "themes"},
    "FPS": {"id": 5, "type": "genres"},
    "Shooter": {"id": 5, "type": "genres"},
    "Puzzle": {"id": 9, "type": "genres"},
    "Visual Novel": {"id": 34, "type": "genres"},
    "Anime": {"id": 34, "type": "genres"},
    "Platformer": {"id": 8, "type": "genres"},
    "Racing": {"id": 10, "type": "genres"},
    "Sports": {"id": 14, "type": "genres"},
    "Sandbox": {"id": 33, "type": "themes"},
    "Survival": {"id": 21, "type": "themes"},
    "Stealth": {"id": 23, "type": "themes"},
    "Mystery": {"id": 43, "type": "themes"},
    "Fighting": {"id": 4, "type": "genres"},
    "Point & Click": {"id": 2, "type": "genres"},
    "Hack and Slash": {"id": 25, "type": "genres"},
    "MOBA": {"id": 36, "type": "genres"},
    "Card Game": {"id": 35, "type": "genres"},
    "Comedy": {"id": 27, "type": "themes"},
    "Historical": {"id": 22, "type": "themes"},
    "Romance": {"id": 44, "type": "themes"}
}

api = os.getenv("STEAM_API_KEY")
url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"

def user_profile(steam_id: str) -> list:
    params = {
        "key": api,
        "steamid": steam_id,
        "include_appinfo": 1,
        "include_free_played_games": 1
    }
    response = requests.get(url, params = params)
    data = response.json()
    api_response = data.get("response", {})

    # Check if account details are private
    if not api_response or "games" not in api_response:
        raise ValueError("Could not retrieve game data for SteamID ${steam_id}. The user's profile, game library, or playtime settings are likely set to Private.")
    
    all_games = api_response.get("games", [])

    sorted_games = sorted(
        all_games, 
        key=lambda x: x.get("playtime_forever", 0), 
        reverse=True
    )

    top_games = sorted_games[:5]
    top5 = []

    for game in top_games:
        top5.append({
            "name": game.get("name"),
            "appid": game.get("appid"),
            "playtime": game.get("playtime_forever", 0)
        })

    return top5

def get_game_tags(appid: int) -> tuple:
    """Fetches Steam tags, filters them against IGDB, and returns the top 3."""
    try:
        url = f"https://steamspy.com/api.php?request=appdetails&appid={appid}"
        response = requests.get(url)
        data = response.json()
        tags_dict = data.get("tags", {})
        
        valid_tags = []
        
        # tags_dict keys are ordered by most votes on SteamSpy
        for steam_tag in tags_dict.keys():
            if steam_tag in STEAM_TO_IGDB_MAP:
                # We save it as a string formatted like "12:genres" or "18:themes"
                # This makes it super easy to split and use in your IGDB script later
                igdb_info = STEAM_TO_IGDB_MAP[steam_tag]
                formatted_tag = f"{igdb_info['id']}:{igdb_info['type']}"
                
                valid_tags.append(formatted_tag)
                
            # Stop once we have 3 valid, IGDB-compatible tags
            if len(valid_tags) == 3:
                break
                
        # If a game has fewer than 3 valid tags, pad the rest with None
        while len(valid_tags) < 3:
            valid_tags.append(None)
            
        # Return as a tuple: (tag1, tag2, tag3)
        return tuple(valid_tags)
        
    except Exception:
        # If SteamSpy fails, return Nones
        return (None, None, None)