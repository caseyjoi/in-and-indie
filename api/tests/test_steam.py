import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock, ANY
import sqlalchemy as db

# ── Path setup ────────────────────────────────────────────────────────────────
# Python needs to know where our source modules live.
# We resolve the project root from this file's location and add both
# source folders so `from Steam import ...` and `from DB import ...` work.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "db_conn"))

# Import the function we'll be testing
from steam import user_profile, get_game_tags


# ─────────────────────────────────────────────────────────────────────────────
# UNIT TEST
# A unit test checks one function in complete isolation.
# Every external dependency (network calls, keyboard input) is replaced with
# a controlled fake so the test never touches the real world.
# ─────────────────────────────────────────────────────────────────────────────
class TestUnplayedGames(unittest.TestCase):

    # @patch swaps out a real object with a MagicMock for the duration of the test.
    # Decorators stack bottom-up, so the bottom decorator's mock is the first
    # argument after `self`, the next one is second, and so on.
    @patch("steam.requests.get")       # replaces the Steam API client factory
    def test_get_user_info(self, mock_build):
        # Fake API Response
        fake_items = [
            {'name': 'Game 1', 'appid': 100, 'playtime_forever': 10},
            {'name': 'Game 2', 'appid': 200, 'playtime_forever': 80},
            {'name': 'Game 3', 'appid': 300, 'playtime_forever': 60},
            {'name': 'Game 4', 'appid': 400, 'playtime_forever': 70},
            {'name': 'Game 5', 'appid': 500, 'playtime_forever': 100},
            {'name': 'Game 6', 'appid': 600, 'playtime_forever': 60}
        ]

        # Fake a proper result
        fake_result = [
            {'name': 'Game 5', 'appid': 500, 'playtime': 100},
            {'name': 'Game 2', 'appid': 200, 'playtime': 80},
            {'name': 'Game 4', 'appid': 400, 'playtime': 70},
            {'name': 'Game 3', 'appid': 300, 'playtime': 60},
            {'name': 'Game 6', 'appid': 600, 'playtime': 60}
        ]

        # Wire the mock so requests.get(url).json() returns our fake data
        mock_steam = MagicMock()
        mock_steam.status_code = 200
        mock_steam.json.return_value = {"response": {"games": fake_items}} # Match Steam's actual JSON structure
        mock_build.return_value = mock_steam

        # Call the real function using a dummy User ID
        result = user_profile("123456")

        # Print to terminal
        print(f"\nUser Profile Output:\n{result}")

        # The function should return the items list exactly as the API gave them
        self.assertEqual(result, fake_result)

        # Verify requests.get was used
        mock_build.assert_called_once()

    @patch("steam.requests.get")
    def test_get_game_tags(self, mock_get):
        # Fake SteamSpy response with some valid tags, and some useless ones
        mock_steamspy = MagicMock()
        mock_steamspy.json.return_value = {
            "tags": {
                "RPG": 500,        # Valid (Should become '12:genres')
                "Cute": 400,       # Invalid (Should be ignored)
                "Action": 300,     # Valid (Should become '1:themes')
                "Funny": 200,      # Invalid (Should be ignored)
                "Sci-fi": 100      # Valid (Should become '18:themes')
            }
        }
        mock_get.return_value = mock_steamspy
        
        result = get_game_tags(12345)
        
        print(f"\nFiltered Tags Output:\n{result}")
        
        # It should ignore Cute and Funny, returning exactly the 3 valid IGDB tags
        self.assertEqual(result, ("12:genres", "1:themes", "18:themes"))
        
if __name__ == "__main__":
    unittest.main()