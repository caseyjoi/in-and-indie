import os
import requests
from dotenv import load_dotenv
load_dotenv()

def get_rating(game_name):
    client_id = os.getenv("IGDB_CLIENT_ID")
    client_secret = os.getenv("IGDB_CLIENT_SECRET")

    url = f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials"
    response = requests.post(url)
    token_data = response.json()
    access_token = token_data.get("access_token")

    headers = {
        'Client-ID': client_id,
        'Authorization': f'Bearer {access_token}'
    }
    body = f'fields name, rating, game_type; search "{game_name}"; where version_parent = null & game_type = 0; limit 1;'
    rating_response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body)

    data = rating_response.json()
    if data and len(data) > 0:
        # print(game_name) Used for testing only
        rating = data[0].get("rating")
        if rating is None:
            return None
        return round(rating/10, 1)
    else:
        return None

def get_recommendations(top_tags: list) -> list:
    """
    Takes a list of formatted tag strings (e.g., ["12:genres", "18:themes"] and returns top 5 indie games with those tags plus their genres and Steam Store links.
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

    genre_ids = []
    theme_ids = []

    for tag in top_tags:
        if not tag:
            continue
        tag_id, category = tag.split(":") 
        if category == "genres":
            genre_ids.append(tag_id)
        elif category == "themes":
            theme_ids.append(tag_id)

    # Must be Indie (Genre 32), category 0 (Main Game), rating must exist
    where_clauses = ["genres = [32]", "category = 0", "rating != null"]

    if genre_ids:
        genres_string = ",".join(genre_ids)
        where_clauses.append(f"genres = ({genres_string})")

    if theme_ids:
        themes_string = ",".join(theme_ids)
        where_clauses.append(f"themes = ({themes_string})")

    final_where = " & ".join(where_clauses)

    # Added genres.name and websites to the query
    body = f"fields name, rating, cover.url, genres.name, websites.category, websites.url; where {final_where}; sort rating desc; limit 5;"
    rating_response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body)
    raw_data = rating_response.json()
    clean_recommendations = []
    
    # Parse the data to be frontend-ready
    for game in raw_data:
        # 1. Format Rating
        rating = game.get("rating")
        formatted_rating = round(rating / 10, 1) if rating else "N/A"
        
        # 2. Format Cover URL
        cover_data = game.get("cover", {})
        cover_url = cover_data.get("url", "No cover available")
        if cover_url.startswith("//"):
            cover_url = "https:" + cover_url

        # 3. Extract Genre Names (Combine them into a single string: "Action, RPG")
        genres_list = game.get("genres", [])
        genre_names = [g.get("name") for g in genres_list if g.get("name")]
        genres_string = ", ".join(genre_names) if genre_names else "Indie"

        # 4. Extract Steam Link (IGDB Website Category 13 is Steam)
        websites_list = game.get("websites", [])
        steam_url = "#" # Default fallback
        for site in websites_list:
            if site.get("category") == 13:
                steam_url = site.get("url")
                break # Found Steam, stop looking

        clean_recommendations.append({
            "name": game.get("name", "Unknown Game"),
            "rating": formatted_rating,
            "cover_url": cover_url,
            "genres": genres_string,
            "steam_link": steam_url
        })
        
    return clean_recommendations