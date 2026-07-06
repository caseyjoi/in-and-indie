import re 
import requests 
import pandas as pd
import sqlalchemy as db
from urllib.parse import urlparse
import os
from pathlib import Path
from dotenv import load_dotenv

script_dir = Path(__file__).resolve().parent
env_path = script_dir / '.env'
load_dotenv(dotenv_path=env_path)

# -------------------------------------------------------------------------------
#First steps: regex for steam url, calling Google Search API, filtering results using regex check.
#Example STEAM shop url: https://store.steampowered.com/app/1174180/Red_Dead_Redemption_2/
# -------------------------------------------------------------------------------

# ----- Helper method to pull Steam ID from given url parameter, returns ID if found, else None.
def extract_steam_id(url):
    if not url:
        return None
    
    if "store.steampowered.com/app/" not in url.lower():
        return None
    
    parsed_url_path = urlparse(url).path
    match = re.search(r'/app/(\d+)', parsed_url_path)

    return match.group(1) if match else None

# ----- Method that utilizes Brave search API to find Steam shop urls.
#       Returns array of game IDs. 
def find_new_game_id():

    api_key = os.getenv("BRAVE_SEARCH_API")

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


# ----- Method that utilizes Steam's internal API to fetch game metadata, app_id as parameter. 
#       Returns dictionary of metadata for game.
def get_game_metadata(app_id):
    
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"

    try: 
        response = requests.get(url)
        response.raise_for_status()
        data = response.json() 

        if data and data.get(app_id, {}).get('success'):
            game_data = data[app_id]['data']

            metadata = {
                "id": app_id,
                "title": game_data.get("name"),
                "summary": game_data.get("short_description"),
                "publishers": str(game_data.get("publishers", ["Unknown"])), #to str bc lists can't be inserted into sql
                "price": game_data.get("price_overview", {}).get("final_formatted", "Free/TBD"),
                "release_date": game_data.get("release_date", {}).get("date", "TBD")
            }
            return metadata
    except Exception as e: 
        print(f"Failed fetching metadata for ID {app_id}: {e}")
   
    return None

# ----- Method that utilizes Steam Web API to fetch game news, app_id as parameter. 
#       Returns list of dictionary objects associated with news article. 
def get_game_news(app_id):

    url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002"
    params = {"appid": app_id, "count": 3, "maxlength":150}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json() 

        news_items = data.get("appnews", {}).get("newsitems", [])

        feed = []
        for item in news_items:
            feed.append({
                "title": item.get("title"),
                "author": item.get("author"),
                "url": item.get("url"),
                "contents": item.get("contents")
            })
        return feed
    
    except Exception as e: 
        print(f"Failed fetching news for ID {app_id}: {e}")
    
    return []

# -------------------------------------------------------------------------------
# Storing metadata into a database. {ID, Title, Publisher, Price, Release Date}
# -------------------------------------------------------------------------------

# ----- Method that inserts metadata into metadataDB, takes in dictionary of game metadata. 
#       Database columns are: "id", "title", "summary", "publishers", "price", "release_date"
def add_to_db(gameMetadata):

  try:
      metadataDF = pd.DataFrame.from_dict([gameMetadata])
      engine = db.create_engine("sqlite:///data/metadataDB.db")
      metadataDF.to_sql(
        "metadata", 
        con=engine, 
        if_exists = "append", #set parameter to "replace" inorder to reset db
        index=False
        )

  except Exception as e: 
      print(f"Failed to add metadata into database for {gameMetadata}: {e}")

# ----- Method that returns metadata from metadataDB, takes in gameID.
#       Returns dictionary from data frame.
def get_from_db(app_id): 
    try:
        engine = db.create_engine("sqlite:///data/metadataDB.db")

        query = "SELECT * FROM metadata WHERE id = :app_id"
        df = pd.read_sql_query(db.text(query), con=engine, params={"app_id": str(app_id)})

        if not df.empty:
            return df.iloc[0].to_dict() 
    
    except Exception as e:
        print(f"Failed to fetch metadata from database for ID {app_id}: {e}")

    return None 

# ----- Method that returns whether id is in the database, takes in gameID.
#       Returns True or False
def is_in_db(app_id):
    try: 
        engine = db.create_engine("sqlite:///data/metadataDB.db")
        
        query = "SELECT * FROM metadata WHERE id = :app_id"
        df = pd.read_sql_query(db.text(query), con=engine, params={"app_id": str(app_id)})

        if df.empty:
            return False

        else:
            return True


    except Exception as e:
        print(f"Failed to read metadata from database for ID {app_id}: {e}")

# -------------------------------------------------------------------------------
# Now, utilize YT/Reddit/Search APIs to find communities: 
# -------------------------------------------------------------------------------

# Unfortunately we didn't have time to implement this feature :( 

# -------------------------------------------------------------------------------
# Last helper methods for UI/CLI
# -------------------------------------------------------------------------------

# ----- Helper method that prompts for user input, and continues to do so until valid.
#       Returns string user_input.
def prompt_user(input_prompt, list_of_valid_responses):
    valid = False

    while not valid:
        user_input = input(input_prompt)

        for valid_response in list_of_valid_responses:
            if user_input == valid_response: 
                valid = True
                break
        
        if not valid:
          print(f"Please enter a valid response.")
    
    return str(user_input)

# ----- Helper method that prompts the user if they want to see more games.
#       Returns True or False. 
def should_we_continue(page):
    user_input = prompt_user(f"\nPage {page}. Would you like to see more games? [Y/N]\n", ["Y", "N"])
    if user_input == "Y":
        return True
    elif user_input == "N":
        return False
    else:
        return False 

# ----- Helper method that grabs a unique page from the db to allow cycling of games. 
#       Returns page. 
def get_page_from_db(limit=10, offset=0):
    try: 
        engine = db.create_engine("sqlite:///data/metadataDB.db")
        query = "SELECT * FROM metadata LIMIT :limit OFFSET :offset" 

        df = pd.read_sql_query(db.text(query), con=engine, params={"limit": limit, "offset": offset})
        return df.to_dict(orient="records")
    except Exception as e: 
        print(f"Failed to fetch page from database: {e}")
    
    return []


# -------------------------------------------------------------------------------
# Streamline CLI expereince for user (call methods):
# -------------------------------------------------------------------------------


# THIS DOES CALL API, BE CAREFUL! 
if __name__ == "__main__":
    start = input("\nWelcome to In and Indie!\nEnter any key to see a list of up and coming games.\n")

    print("\n...loading...\n")

    discovered_ids = find_new_game_id()

    for app_id in discovered_ids:
        if not is_in_db(app_id):
            add_to_db(get_game_metadata(app_id))

    offset = 0
    continuing = True

    while continuing:
        
        page = get_page_from_db(limit=10, offset=offset)

        if not page:
            print ("\nNo more games to show!")
            break

        discovered_ids = [g["id"] for g in page]

        for number, meta in enumerate(page): 
            print("=" * 60)

            print(f"[ {number} ]")
            print(f"TITLE:        {meta['title']} (ID: {meta['id']})")
            print(f"RELEASE DATE: {meta['release_date']}")
            print(f"PUBLISHER:    {meta['publishers']}")
            print(f"PRICE:        {meta['price']}")
            print(f"SUMMARY:      {meta['summary']}")


        print("=" * 60)
        continue_input = prompt_user("\nDo any of the games above interest you? [Y/N]\n", ["Y", "N"])

        if continue_input == "Y":
            game_index = int(prompt_user("\nPlease enter the index of the game you are interested in. [0-9]\n", ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]))
            news_feed = get_game_news(discovered_ids[game_index])

            print(f"")
            print("=" * 60)
            print(f"Here is more information for {get_from_db(discovered_ids[game_index])['title']}:\n")

            if news_feed:
                print(f"LATEST ARTICLE:     \"{news_feed[0]['title']}\"")
                #can also print out [1] and [2], for now
                print(f"READ UPDATE:        {news_feed[0]['url']}")
            else:
                print("LATEST ARTICLE: No recent updates posted.")

            print(f"COMMUNITY LINKS:    To be implemented.")
            print("=" * 60)
            offset += 10
            continuing = should_we_continue(offset // 10)
        
        elif continue_input == "N":
            offset += 10
            continuing = should_we_continue(offset // 10)