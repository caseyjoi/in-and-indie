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

app = Flask(__name__)

@app.route('/api/recommendations/<steam_id>', methods=['GET'])
def get_recommendations(steam_id):
    """
    The main endpoint React will call. 
    Usage: fetch('/api/recommendations/76561198924137021')
    """
    try:
        # Save and update user data, first time users saved while returning users load from cache
        DB.save_to_db(steam_id)
        df_top_games = DB.update_game(steam_id)
        
        if df_top_games is None or df_top_games.empty:
            return jsonify({"error": "No games found or Steam profile is private."}), 404

        # Convert Pandas to a list of dicts for JSON
        user_games = df_top_games.to_dict(orient="records")

        # Check most played games for common tags
        top_tags = DB.aggregate_tags(steam_id)
        if not top_tags:
            return jsonify({"error": "Not enough data to find favorite tags."}), 404

        # Get recommendations from IGDB
        recommendations = igdb.get_recommendations(top_tags)

        # Add YouTube trailers
        for rec in recommendations:
            rec["trailer_url"] = get_trailer_url(rec["name"])
            # PLACEHOLDER Brave Search function
            rec["community_links"] = [] 

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
    app.run(debug=True, host='0.0.0.0', port=5000)