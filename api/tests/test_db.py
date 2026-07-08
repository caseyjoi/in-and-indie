import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import sqlalchemy as db

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "scripts"))
sys.path.insert(0, str(project_root / "db_conn"))

import DB


class TestUpdateGame(unittest.TestCase):

    @patch("DB._default_engine")
    @patch("DB.get_trailer_url")
    @patch("DB.get_game_tags")
    @patch("DB.get_rating")
    def test_update_game(self, mock_rating, mock_tags, mock_trailer, mock_engine):
        seed = [
            {"name": "Game A", "appid": 10, "user_steam_id": "u1", "playtime": 0,
             "tag1": None, "tag2": None, "tag3": None,
             "igdb_rating": None, "trailer": None},
            {"name": "Game B", "appid": 20, "user_steam_id": "u1", "playtime": 5,
             "tag1": None, "tag2": None, "tag3": None,
             "igdb_rating": None, "trailer": None},
            {"name": "Game C", "appid": 30, "user_steam_id": "u1", "playtime": 5,
             "tag1": None, "tag2": None, "tag3": None,
             "igdb_rating": None, "trailer": None},
            {"name": "Other", "appid": 99, "user_steam_id": "u2", "playtime": 0,
             "tag1": None, "tag2": None, "tag3": None,
             "igdb_rating": None, "trailer": None},
        ]
        ratings = {"Game A": 7.0, "Game B": 9.0, "Game C": 8.0, "Other": 1.0}

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            engine = db.create_engine(f"sqlite:///{db_path}")
            pd.DataFrame(seed).to_sql("top5", con=engine,
                                      if_exists="replace", index=False)

            mock_engine.return_value = engine
            mock_rating.side_effect = lambda name: ratings[name]
            mock_tags.return_value = ("12:genres", "18:themes", "1:themes")
            mock_trailer.side_effect = lambda name: f"https://www.youtube.com/watch?v={name.replace(' ', '_')}"

            result = DB.update_game("u1", limit=2)

            self.assertEqual(list(result["name"]), ["Game B", "Game C", "Game A"])
            self.assertEqual(list(result["igdb_rating"]), [9.0, 8.0, 7.0])

            by_name = result.set_index("name")
            self.assertEqual(by_name.loc["Game B", "tag1"], "12:genres")
            self.assertEqual(by_name.loc["Game C", "tag1"], "12:genres")
            self.assertTrue(pd.isna(by_name.loc["Game A", "tag1"]))

            self.assertEqual(by_name.loc["Game B", "trailer"], "https://www.youtube.com/watch?v=Game_B")
            self.assertEqual(by_name.loc["Game C", "trailer"], "https://www.youtube.com/watch?v=Game_C")
            self.assertTrue(pd.isna(by_name.loc["Game A", "trailer"]))

            self.assertEqual(mock_trailer.call_count, 2)
            self.assertEqual(mock_tags.call_count, 2)

            other = pd.read_sql(
                "SELECT * FROM top5 WHERE user_steam_id = 'u2'", con=engine
            )
            self.assertTrue(other["igdb_rating"].isna().all())
            self.assertTrue(other["tag1"].isna().all())
        finally:
            engine.dispose()
            os.remove(db_path)


if __name__ == "__main__":
    unittest.main()
