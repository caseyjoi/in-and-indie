import unittest
from unittest.mock import patch, MagicMock
import requests
import pandas as pd
from main import extract_steam_id, find_new_game_id, get_game_metadata, get_game_news, add_to_db, get_from_db, get_page_from_db, is_in_db


class TestStreamFetchFlow(unittest.TestCase):

    # Basic UNIT TESTING for most methods.

    # extract_steam_id(url): 

    # Valid URL.
    def test_extract_steam_id_valid_url(self):
        url = "https://store.steampowered.com/app/1174180/Red_Dead_Redemption_2/"
        self.assertEqual(extract_steam_id(url), "1174180")

    # Bad domain, id.
    def test_extract_steam_id_invalid(self):
        url = "https://store.epicgames.com/p/1234/red-dead-redemption-2"
        self.assertIsNone(extract_steam_id(url))

    # Correct domain, no id.
    def test_extract_steam_id_no_id(self):
        url = "https://store.steampowered.com/app/abc/"
        self.assertIsNone(extract_steam_id(url))

    # None input.
    def test_extract_steam_id_none_input(self):
        self.assertIsNone(extract_steam_id(None))

    # Empty input.
    def test_extract_steam_id_empty_string(self):
        self.assertIsNone(extract_steam_id(""))

    # find_new_game_id():

    # Tests with valid Brave API response.
    @patch('main.requests.get')
    def test_find_new_game_id_success(self, mock_get):
        # Setup the mock response object
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {"url": "https://store.steampowered.com/app/12345/GameA/"}
                ]
            }
        }
        mock_get.return_value = mock_response

        result = find_new_game_id()
        self.assertIn("12345", result)
    
    # Tests with network error / exception. 
    @patch('main.requests.get')
    def test_find_new_game_id_api_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error.")
        result = find_new_game_id()
        self.assertEqual(result, [])

    # Tests with no url field. 
    @patch('main.requests.get')
    def test_find_new_game_id_none_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "web": {
                "results": [
                    {"url": None},
                    {"url": "https://store.steampowered.com/app/12345/GameA/"}
                ]
            }
        }
        mock_get.return_value = mock_response
        result = find_new_game_id()
        self.assertIn("12345", result)
        self.assertNotIn(None, result)


    # get_game_metadata(app_id)

    # Tests with valid Internal Steam API response. 
    @patch('main.requests.get')
    def test_get_game_metadata_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "12345": {
                "success": True,
                "data": {
                    "name": "Test Game",
                    "short_description": "Test.",
                    "publishers": ["Studio"],
                    "price_overview": {"final_formatted": "$14.99"},
                    "release_date": {"date": "July 8, 2026"}
                }
            }
        }
        mock_get.return_value = mock_response

        meta = get_game_metadata("12345")
        self.assertEqual(meta["title"], "Test Game")
        self.assertEqual(meta["price"], "$14.99")

    # Tests with network error / exception. 
    @patch('main.requests.get')
    def test_get_game_metadata_api_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error.")
        result = get_game_metadata("12345")
        self.assertIsNone(result)


    # get_game_news(app_id):

    #Tests with valid Steam API response. 
    @patch('main.requests.get')
    def test_get_game_news_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "appnews": {
                "newsitems": [
                    {
                        "title": "Community Update",
                        "author": "Studio",
                        "url": "https://store.steampowered.com/news/123",
                        "contents": "Check out gkdlskfds"
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        feed = get_game_news("12345")
        
        self.assertEqual(len(feed), 1)
        self.assertEqual(feed[0]["title"], "Community Update")
        self.assertEqual(feed[0]["author"], "Studio")
    
    # Tests with network error / exception. 
    @patch('main.requests.get')
    def test_get_game_news_api_failure(self, mock_get):
        mock_get.side_effect = Exception("Network error.")
        result = get_game_news("12345")
        self.assertEqual(result, [])


    # add_to_db(gameMetadata):

    # Tests with valid metadata. 
    @patch('main.db.create_engine')
    def test_add_to_db_success(self, mock_engine):
        mock_conn = MagicMock()
        mock_engine.return_value = mock_conn
        with patch('main.pd.DataFrame.to_sql') as mock_to_sql:
            metadata = {
                "id": "12345",
                "title": "Test Game",
                "summary": "A test.",
                "publishers": "['Studio']",
                "price": "$9.99",
                "release_date": "July 8, 2026"
            }
            try:
                add_to_db(metadata)
            except Exception:
                self.fail("add_to_db raised an exception on valid input.")

    # Tests when engine throws exception. 
    @patch('main.db.create_engine')
    def test_add_to_db_failure(self, mock_engine):
        mock_engine.side_effect = Exception("DB error")
        metadata = {"id": "12345", "title": "Test Game", "summary": "", "publishers": "", "price": "", "release_date": ""}
        try:
            add_to_db(metadata)
        except Exception:
            self.fail("add_to_db should handle exceptions without crashing.")
    
    # get_from_db(app_id): 

    # Tests with valid entry in db.
    @patch('main.db.create_engine')
    def test_get_from_db_success(self, mock_engine):
        mock_conn = MagicMock()
        mock_engine.return_value = mock_conn
        fake_row = {"id": "12345", "title": "Test Game", "summary": "A test.", "publishers": "['Studio']", "price": "$9.99", "release_date": "July 8, 2026"}
        with patch('main.pd.read_sql_query') as mock_read:
            mock_read.return_value = pd.DataFrame([fake_row])
            result = get_from_db("12345")
            self.assertEqual(result["title"], "Test Game")
            self.assertEqual(result["price"], "$9.99")
    
    # Tests with invalid entry in db. 
    @patch('main.db.create_engine')
    def test_get_from_db_not_found(self, mock_engine):
        mock_conn = MagicMock()
        mock_engine.return_value = mock_conn
        with patch('main.pd.read_sql_query') as mock_read:
            mock_read.return_value = pd.DataFrame()
            result = get_from_db("99999")
            self.assertIsNone(result)
    
    # Tests when db read fails. 
    @patch('main.db.create_engine')
    def test_get_from_db_failure(self, mock_engine):
        mock_engine.side_effect = Exception("DB error")
        result = get_from_db("12345")
        self.assertIsNone(result)

    # Basic INTEGRATION TESTING for initial four methods. ----------------------------------

    # Brave API -> ID -> Metadata -> News
    @patch('main.requests.get')
    def test_game_pipeline_integration(self, mock_get):

        # Build responses for each API (Brave, Steam, Internal Steam)
        brave_response = {
            "web": {
                "results": [{"url": "https://store.steampowered.com/app/99999/SpecGame/"}]
            }
        }
        
        steam_meta_response = {
            "99999": {
                "success": True,
                "data": {
                    "name": "Integration Title",
                    "short_description": "Testing the data flow.",
                    "publishers": ["Pipeline Corp"],
                    "price_overview": {"final_formatted": "$29.99"},
                    "release_date": {"date": "Coming Soon"}
                }
            }
        }
        
        steam_news_response = {
            "appnews": {
                "newsitems": [{"title": "Integration Update", "author": "QA Team", "url": "http://news.link", "contents": "Content"}]
            }
        }

        # Grab correct order of mock responses.
        mock_brave_obj = MagicMock()
        mock_brave_obj.json.return_value = brave_response
        
        mock_meta_obj = MagicMock()
        mock_meta_obj.json.return_value = steam_meta_response
        
        mock_news_obj = MagicMock()
        mock_news_obj.json.return_value = steam_news_response
        
        mock_get.side_effect = [mock_brave_obj, mock_brave_obj, mock_meta_obj, mock_news_obj]

        # LARP the pipeline: 
        discovered_ids = find_new_game_id()
        self.assertIn("99999", discovered_ids) #Checks ID 

        
        target_id = discovered_ids[0]
        
        # Pull metadata using the extracted ID
        metadata_result = get_game_metadata(target_id)
        self.assertIsNotNone(metadata_result)
        self.assertEqual(metadata_result["title"], "Integration Title")
        
        # Pull news feed using ID
        news_result = get_game_news(target_id)
        self.assertEqual(len(news_result), 1)
        self.assertEqual(news_result[0]["title"], "Integration Update")
    
    # Testing database pipeline. 
    @patch('main.pd.read_sql_query')
    @patch('main.pd.DataFrame.to_sql')
    @patch('main.db.create_engine')
    @patch('main.requests.get')
    def test_metadata_db_pipeline(self, mock_get, mock_engine, mock_to_sql, mock_read):
        mock_response = MagicMock() 
        mock_response.json.return_value = {
            "99999": {
                "success": True,
                "data": {
                    "name": "DB Pipeline Game",
                    "short_description": "Testing db flow.",
                    "publishers": ["Studio"],
                    "price_overview": {"final_formatted": "$19.99"},
                    "release_date": {"date": "Coming Soon"}
                }
            }
        }

        mock_get.return_value = mock_response

        # grab metadata from mock json 
        meta = get_game_metadata("99999")
        self.assertIsNotNone(meta)
        self.assertEqual(meta["title"], "DB Pipeline Game")

        # insert into db
        add_to_db(meta)
        self.assertTrue(mock_to_sql.called)

        # mock db read 
        mock_read.return_value = pd.DataFrame([meta])
        stored = get_from_db("99999")
        self.assertEqual(stored["title"], "DB Pipeline Game")
        self.assertEqual(stored["price"], "$19.99")
        
    # Testing full pipeline. 
    @patch('main.pd.read_sql_query')
    @patch('main.db.create_engine')
    @patch('main.requests.get')
    def test_full_pipeline_brave_to_new(self, mock_get, mock_engine, mock_read):
        brave_response = {
            "web": {
                "results": [{"url": "https://store.steampowered.com/app/77777/FullGame/"}]
            }
        }

        meta_response = { 
            "77777": { 
                "success": True, 
                "data": {
                    "name": "Full Pipeline Game",
                    "short_description": "End to end test.",
                    "publishers": ["Studio"],
                    "price_overview": {"final_formatted": "$24.99"},
                    "release_date": {"date": "August 2026"}
                }
            }
        }

        news_response = { 
            "appnews": {
                "newsitems": [{"title": "Launch Trailer", "author": "Studio", "url": "http://news.link", "contents": "Content"}]
            }
        }

        mock_brave = MagicMock()
        mock_brave.json.return_value = brave_response
        mock_meta = MagicMock()
        mock_meta.json.return_value = meta_response
        mock_news = MagicMock()
        mock_news.json.return_value = news_response

        # set up calls in order 
        mock_get.side_effect = [mock_brave, mock_brave, mock_meta, mock_news]

        discovered_ids = find_new_game_id()
        self.assertIn("77777", discovered_ids)

        # metadata
        meta = get_game_metadata(discovered_ids[0])
        self.assertIsNotNone(meta)
        self.assertEqual(meta["title"], "Full Pipeline Game")

        # mock db storing and retrieving it
        mock_read.return_value = pd.DataFrame([meta])
        stored = get_from_db(discovered_ids[0])
        self.assertEqual(stored["title"], "Full Pipeline Game")

        # fetch news
        news = get_game_news(discovered_ids[0])
        self.assertEqual(news[0]["title"], "Launch Trailer")
