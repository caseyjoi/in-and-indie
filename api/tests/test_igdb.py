import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
import sqlalchemy as db

# ── Path setup ────────────────────────────────────────────────────────────────
# Python needs to know where our source modules live.
# We resolve the project root from this file's location and add both
# source folders so `from IGDB import ...` and `from DB import ...` work.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "db_conn"))

# Import the function we'll be testing
from igdb import get_rating, get_recommendations


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TEST
# A unit test checks one function in complete isolation.
# Every external dependency (network calls, keyboard input) is replaced with
# a controlled fake so the test never touches the real world.
# ─────────────────────────────────────────────────────────────────────────────
class TestIGDBRating(unittest.TestCase):

    # @patch swaps out a real object with a MagicMock for the duration of the test.
    # Decorators stack bottom-up, so the bottom decorator's mock is the first
    # argument after `self`, the next one is second, and so on.
    @patch("igdb.requests.post")       # replaces the IGDB API client factory
    def test_get_game_rating(self, mock_post):
        # Fake Authorization response for token and rating
        mock_auth_response = MagicMock()
        mock_auth_response.json.return_value = {"access_token": "fake_token_123"}
        
        mock_data_response = MagicMock()
        mock_data_response.json.return_value = [{"total_rating": 85.5}]

        # Check the URL to see if its an auth response or a rating response and assign it
        def mock_post_side_effect(url, *args, **kwargs):
            if "oauth2/token" in url:
                return mock_auth_response
            elif "v4/games" in url:
                return mock_data_response
            return MagicMock()
        mock_post.side_effect = mock_post_side_effect

        # Call the real function
        result = get_rating("The Witcher 3")
        print(result)

        # Rating is divided by ten then rounded to one decimal point
        self.assertEqual(result, 8.6)
        
        # Verify that two POST requests were made
        self.assertEqual(mock_post.call_count, 2)
    
    @patch("igdb.requests.post")
    def test_get_recommendations(self, mock_post):
        mock_auth = MagicMock()
        mock_auth.json.return_value = {"access_token": "fake_token_123"}
        
        mock_data = MagicMock()
        mock_data.json.return_value = [{
            "name": "Hollow Knight",
            "total_rating": 90.0,
            "genres": [{"name": "Platformer"}],
            "websites": [{"category": 13, "url": "https://store.steampowered.com/app/1"}]
        }]

        def mock_post_side_effect(url, *args, **kwargs):
            if "oauth2/token" in url:
                return mock_auth
            elif "v4/games" in url:
                return mock_data
            return MagicMock()
        mock_post.side_effect = mock_post_side_effect

        result = get_recommendations(["12:genres", "18:themes"])
        print(result)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Hollow Knight")
        self.assertEqual(result[0]["total_rating"], 9.0)
        self.assertEqual(result[0]["genres"], "Platformer")
        self.assertEqual(result[0]["steam_link"], "https://store.steampowered.com/app/1")

if __name__ == "__main__":
    unittest.main()