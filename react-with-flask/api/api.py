# api/api.py
from flask import Flask, jsonify, request
import sys
from pathlib import Path

# Path Setup, since api.py is inside the 'api' folder, 'parent' is the api folder itself.
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root / "scripts"))
sys.path.append(str(project_root / "db_conn"))

# Imports from pipeline
import DB
import igdb
from youtube import get_trailer_url
from brave import find_game_communities
from steam import IGDB_REVERSE_MAP

app = Flask(__name__)

@app.route('/api/recommendations/<steam_id>', methods=['GET'])
def get_recommendations(steam_id):
    """
    The main endpoint React will call. 
    Usage: fetch('/api/recommendations/')
    """
    try:
        # Save and update user data, first time users saved while returning users load from cache
        df_top_games = DB.check_in_db(steam_id)
        
        if df_top_games is None:
            print(f"New user {steam_id}. Fetching from Steam...")
            DB.save_to_db(steam_id)
            df_top_games = DB.update_game(steam_id)
        else:
            print(f"Returning user {steam_id}. Loading from cache...")
        
        if df_top_games is None or df_top_games.empty:
            return jsonify({"error": "No games found or Steam profile is private."}), 404

        # Convert Pandas to a list of dicts for JSON
        user_games = df_top_games.to_dict(orient="records")

        # Translate truncated tags back to real tags
        for game in user_games:
            readable_tags = []
            
            for tag_key in ["tag1", "tag2", "tag3"]:
                raw_tag = game.get(tag_key)
                if raw_tag and raw_tag in IGDB_REVERSE_MAP:
                    readable_tags.append(IGDB_REVERSE_MAP[raw_tag])
                
                # Delete truncated tag from the JSON payload
                game.pop(tag_key, None)
            
            # Removes duplicates
            unique_tags = list(dict.fromkeys(readable_tags))
            
            # Create a "genres" string like the recommendations (e.g., "Fighting, Visual Novel")
            game["genres"] = ", ".join(unique_tags) if unique_tags else "Unknown"

        # Check most played games for common tags
        top_tags = DB.aggregate_tags(steam_id)
        if not top_tags:
            return jsonify({"error": "Not enough data to find favorite tags."}), 404

        # Get recommendations from IGDB
        recommendations = igdb.get_recommendations(top_tags)

        # Add YouTube trailers
        for rec in recommendations:
            rec["trailer_url"] = get_trailer_url(rec["name"])
            
            # Fetch community links from Brave
            community_data = find_game_communities(rec["name"])
            clean_communities = []
            
            # Output is {"reddit": [...], "fandom": [...], "discord": [...]}, grab the Top 1 link to easily map them as buttons
            for platform, links in community_data.items():
                if links and len(links) > 0:
                    top_link = links[0]
                    clean_communities.append({
                        "platform": platform,
                        "title": top_link.get("title"),
                        "url": top_link.get("url")
                    })
                    
            rec["community_links"] = clean_communities

        # Send the JSON to react
        return jsonify({
            "steam_id": steam_id,
            "user_games": user_games,
            "recommendations": recommendations
        })

    except Exception as e:
        # If something crashes, send the error message to React so it can display it
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # host='0.0.0.0' allows external access through Codio's proxy
    app.run(debug=True, host='0.0.0.0', port=5001)