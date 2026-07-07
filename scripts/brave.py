import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("BRAVE_SEARCH_API")

# ----- Method that utilizes Brave search API to find Steam shop urls.
#       Returns array of game IDs. 
def find_new_game_id():

    game_ids = []

    #Prepare API GET request.
    url = "https://api.search.brave.com/res/v1/web/search"

    #Allows multiple unique searches, add more to get more results. Will impact performance. 
    queries = [
        "site:store.steampowered.com/app/ 'Available:' 'explore/upcoming' -'Early Access'",
        "site:store.steampowered.com/app/  'upcoming'"
    ]

    for query in queries:     
        params = {
            "q": query,
            "count": 20 # Max for free Brave Search tier. 
        }

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": api_key
        }
        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            search_data = response.json()
        except Exception as e: 
            print("Brave search failed.")
            return []
        
        #Parse JSON to grab urls, then call helper to scrape game IDs.
        raw_results = search_data.get("web", {}).get("results", [])
        

        for item in raw_results:
            game_url = item.get("url")
            app_id = extract_steam_id(game_url)

            if app_id:
                game_ids.append(app_id)

    
    return game_ids

# ----- Method that utilizes Brave search API to find commmunties related to game name parameter. 
#       Returns dictionary of communities -> currently: "reddit" "fandom" "discord" -> "title" "url" "description"
def find_game_communities(game_name):

    #Prepare API GET request.
    url = "https://api.search.brave.com/res/v1/web/search"
    
    queries = {
        "reddit": f'site:reddit.com "{game_name}"',
        "fandom": f'site:fandom.com "{game_name}"',
        "discord": f'"{game_name}" discord invite site:discord.com OR site:disboard.org'
    }

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key
    }

    communities = {platform: [] for platform in queries}

    for platform, query in queries.items(): 
        params = {
            "q": query,
            "count": 20 # Max for free Brave Search tier. 
        }

        
        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            search_data = response.json()
        except Exception as e: 
            print(f"Brave search failed for {platform}: {e}")
            continue 
        
        #Parse JSON to grab urls, then call helper to scrape game IDs.
        raw_results = search_data.get("web", {}).get("results", [])
        

        for item in raw_results:
            title = item.get("title")
            link = item.get("url")
            description = item.get("description")

            if link:
                communities[platform].append({
                    "title": title, 
                    "url": link,
                    "description": description
                })

    
    return communities


if __name__ == "__main__":
    results = find_game_communities("Hollow Knight")
    for platform, items in results.items():
        print(f"\n--- {platform.upper()} ({len(items)} results) ---")
        for r in items[:5]:
            print(r["url"])