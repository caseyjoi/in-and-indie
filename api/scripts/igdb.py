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
        if not tag: continue
        tag_id, category = tag.split(":") 
        if category == "genres": genre_ids.append(tag_id)
        elif category == "themes": theme_ids.append(tag_id)

    # Must be Indie (Genre 32) and have a cover
    where_parts = ["genres = 32", "cover != null"]
    
    g_ids = [g_id for g_id in genre_ids if g_id != "32"]
    t_ids = theme_ids

    or_logic = []
    if g_ids:
        or_logic.append(f"genres = ({','.join(g_ids)})")
    if t_ids:
        or_logic.append(f"themes = ({','.join(t_ids)})")

    if or_logic:
        combined_or = " | ".join(or_logic)
        where_parts.append(f"({combined_or})")

    final_where = " & ".join(where_parts)
    
    # Sort by 'popularity' instead of rating to make sure there is data
    body = f"fields name, total_rating, cover.url, genres.name, websites.category, websites.url; where {final_where}; sort popularity desc; limit 5;"
    
    print(f"DEBUG QUERY 1: {body}")
    
    response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=body.encode('utf-8'))
    raw_data = response.json()

    # Fallback: If specific search fails, get ANY indie games with covers
    if not isinstance(raw_data, list) or len(raw_data) == 0:
        print("Initial search found nothing. Using fallback...")
        # Just give 5 Indie games with covers
        fallback_body = "fields name, total_rating, cover.url, genres.name, websites.category, websites.url; where genres = 32 & cover != null; limit 5;"
        response = requests.post("https://api.igdb.com/v4/games", headers=headers, data=fallback_body.encode('utf-8'))
        raw_data = response.json()

    clean_recommendations = []
    
    # Parse the data to be frontend-ready
    if isinstance(raw_data, list):
        for game in raw_data:
            # Format Rating
            rating = game.get("total_rating")
            formatted_rating = round(rating / 10, 1) if rating else "N/A"
        
            # Format Cover URL
            cover_data = game.get("cover", {})
            cover_url = cover_data.get("url", "No cover available")
            if cover_url.startswith("//"):
                cover_url = "https:" + cover_url

            # Get Genre Names and put into string, "Action, RPG"
            genres_list = game.get("genres", [])
            genre_names = [g.get("name") for g in genres_list if g.get("name")]
            genres_string = ", ".join(genre_names) if genre_names else "Indie"

            # Get Steam Link (IGDB Website Category 13 is Steam)
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