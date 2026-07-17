import os
import requests
import random
from dotenv import load_dotenv
load_dotenv()

def get_rating(game_name, app_id):
    client_id = os.getenv("IGDB_CLIENT_ID")
    client_secret = os.getenv("IGDB_CLIENT_SECRET")

    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    response = requests.post(url)
    token_data = response.json()
    access_token = token_data.get("access_token")

    # Search external_games using the Steam App ID and grab the score
    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    
    # Look for the Steam ID (uid) in the external games table
    body = f'fields game.rating; where uid = "{app_id}" & external_game_source = 1;'
    
    response = requests.post("https://api.igdb.com/v4/external_games", headers=headers, data=body)
    data = response.json()

    # Data will look like: [{"id": 999, "game": {"id": 123, "rating": 85.5}}]
    if data and len(data) > 0:
        game_obj = data[0].get("game")
        # Ensure game_obj is a dictionary
        if isinstance(game_obj, dict):
            rating = game_obj.get("rating")
            if rating:
                return round(rating / 10, 1)

    # If the Steam ID lookup fails, do name search as a backup
    body = f'fields name, rating, game_type; search "{game_name}"; where version_parent = null & game_type = 0; limit 1;'
    response_name = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body)
    data_name = response_name.json()
    
    if data_name and len(data_name) > 0:
        rating = data_name[0].get("rating")
        return round(rating / 10, 1) if rating else None

    return None

def get_recommendations(top_tags: list) -> list:
    """
    Takes a list of formatted tag strings (e.g., ["12:genres", "18:themes"]) and returns top 5 indie games.
    If less than 5 strict matches are found, pads the rest with top general indie games.
    """
    client_id = os.getenv("IGDB_CLIENT_ID")
    client_secret = os.getenv("IGDB_CLIENT_SECRET")

    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    response = requests.post(url)
    access_token = response.json().get("access_token")

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }

    # Separate tags, ensuring we don't accidentally duplicate 32 (Indie)
    genre_ids = []
    theme_ids = []
    for tag in top_tags:
        if not tag: continue
        tag_id, category = tag.split(":") 
        if tag_id == "32": continue # We manually enforce this below
        if category == "genres": genre_ids.append(tag_id)
        elif category == "themes": theme_ids.append(tag_id)

    # Must be Indie (Genre 32), Main Game (Game Type 0), have >20 reviews
    where_parts = ["genres = (32)", "game_type = 0", "total_rating_count > 20", "platforms = (6)"]

    g_ids = [g for g in genre_ids if g != "32"]
    or_logic = []
    if genre_ids:
        or_logic.append(f"genres = ({','.join(g_ids)})")
    if theme_ids:
        or_logic.append(f"themes = ({','.join(theme_ids)})")

    if or_logic:
        where_parts.append(f"({' | '.join(or_logic)})")

    final_where = " & ".join(where_parts)

    # Sort by total rating
    body = f"fields name, summary, total_rating, cover.image_id, genres.name, themes.name, game_type, platforms, websites.url, websites.type; where {final_where}; sort total_rating desc; limit 100;"
    print(f"DEBUG QUERY 1: {body}")
    response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body.encode('utf-8'))
    raw_data = response.json()

    final_games = []

    # Sort strict matches by how many tags they hit
    if isinstance(raw_data, list) and len(raw_data) > 0:
        target_tags = set(map(int, genre_ids + theme_ids))

        def calculate_match_score(game):
            # Extract genres and themes safely from the API response
            game_genres = {g.get('id') for g in game.get('genres', [])}
            game_themes = {t.get('id') for t in game.get('themes', [])}
            game_tags = game_genres.union(game_themes)

            # Count how many tags intersect with your target list
            match_count = len(game_tags.intersection(target_tags))

            # Tie-breaker: use total_rating (default to 0 if missing)
            rating = game.get('total_rating', 0)

            # Return a tuple: primary sort by matches, secondary sort by rating
            return (match_count, rating)

        # Sort descending and grab top 5
        raw_data.sort(key=calculate_match_score, reverse=True)
        final_games = raw_data[:5] # Grab up to 5

    # Padding: If strict query gave us less than 5 games, fetch other indies to fill the gaps
    if len(final_games) < 5:
        print(f"Only found {len(final_games)} strict matches. Padding the remaining slots...")
        needed_slots = 5 - len(final_games)
        
        # Prevent duplicate games
        existing_ids = [str(g.get("id")) for g in final_games if g.get("id")]
        
        # General highly-rated Indie query
        fallback_where = "genres = (32) & game_type = 0 & total_rating_count > 50"
        if existing_ids:
            fallback_where += f" & id != ({','.join(existing_ids)})"
            
        fallback_body = f"fields name, summary, total_rating, cover.image_id, genres.name, themes.name, game_type, websites.url, websites.type; where {fallback_where}; sort total_rating desc; limit {needed_slots};"
        
        resp = requests.post("https://api.igdb.com/v4/games", headers=headers, data=fallback_body.encode('utf-8'))
        fallback_data = resp.json()
        
        if isinstance(fallback_data, list):
            final_games.extend(fallback_data)

    clean_recommendations = []
    
    # Parse the final list (strict matches + padding)
    for game in final_games:
        rating = game.get("total_rating")
        formatted_rating = round(rating / 10, 1) if rating else "N/A"
    
        cover_data = game.get("cover", {})
        image_id = cover_data.get("image_id")
        cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg" if image_id else "No cover available"

        genres_list = game.get("genres", [])
        genre_names = [g.get("name") for g in genres_list if g.get("name")]
        genres_string = ", ".join(genre_names) if genre_names else "Indie"

        websites_list = game.get("websites", [])
        steam_url = "#" 
        for site in websites_list:
            if site.get("type") == 13:
                steam_url = site.get("url")
                break 

        clean_recommendations.append({
            "name": game.get("name", "Unknown Game"),
            "summary": game.get("summary", "No description available."),
            "rating": formatted_rating,
            "cover_url": cover_url,
            "genres": genres_string,
            "steam_link": steam_url
        })
        
    return clean_recommendations

def get_random_indies(count=3):
    """Fetches a random batch of highly-rated indie games using pagination offset."""
    client_id = os.getenv("IGDB_CLIENT_ID")
    client_secret = os.getenv("IGDB_CLIENT_SECRET")

    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    access_token = requests.post(url).json().get("access_token")

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }

    # There are easily 300+ highly-rated indie games, pick a random starting point.
    random_offset = random.randint(0, 300)
    
    where_clause = "genres = (32) & game_type = 0 & total_rating_count > 20 & platforms = (6)"
    body = f"fields name, summary, total_rating, cover.image_id, genres.name, themes.name, websites.url, websites.type; where {where_clause}; sort total_rating desc; limit {count}; offset {random_offset};"
    
    response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body.encode('utf-8'))
    raw_data = response.json()
    
    clean_randoms = []
    if isinstance(raw_data, list):
        for game in raw_data:
            rating = game.get("total_rating")
            
            cover_data = game.get("cover", {})
            image_id = cover_data.get("image_id")
            
            genres_list = game.get("genres", [])
            genre_names = [g.get("name") for g in genres_list if g.get("name")]
            
            steam_url = "#" 
            for site in game.get("websites", []):
                if site.get("type") == 13:
                    steam_url = site.get("url")
                    break 

            clean_randoms.append({
                "name": game.get("name", "Unknown Game"),
                "summary": game.get("summary", "No description available."),
                "rating": round(rating / 10, 1) if rating else "N/A",
                "cover_url": f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg" if image_id else "No cover available",
                "genres": ", ".join(genre_names) if genre_names else "Indie",
                "steam_link": steam_url
            })
            
    return clean_randoms