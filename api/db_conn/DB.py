import requests
import pandas as pd
from pandas.errors import DatabaseError
import sqlalchemy as db
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
import sys
import json, pathlib
from collections import Counter
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
scripts_dir  = project_root / "scripts"
sys.path.append(str(project_root))
sys.path.append(str(scripts_dir))
from steam import user_profile, get_game_tags
from igdb import get_rating
from youtube import get_trailer_url

def _default_engine():
    return db.create_engine(f"sqlite:///{project_root / 'db_conn' / 'games_cache.db'}")

def save_to_db(steam_id):
    engine = _default_engine()

    games = user_profile(steam_id)
    df = pd.json_normalize(games)

    df["user_steam_id"] = steam_id
    df["tag1"] = None
    df["tag2"] = None
    df["tag3"] = None
    df["igdb_rating"] = None
    df["trailer"] = None

    cols = ["name",
            "appid",
            "user_steam_id",
            "playtime",
            "tag1",
            "tag2",
            "tag3",
            "igdb_rating",
            "trailer"]
    df = df[cols]

    df.to_sql('top5', con = engine, if_exists = 'append', index = False)

def check_in_db(steam_id):
    engine = _default_engine()
    query = "SELECT * FROM top5 WHERE user_steam_id = :steam_id"
    try:
        df = pd.read_sql(query, con = engine, params = {"steam_id": steam_id})
    except (OperationalError, DatabaseError):
        # Fresh/empty DB file with no `top5` table yet. save_to_db will create it.
        return None
    if df.empty:
        return None
    else:
        return df


_NUMERIC_COLS = ["igdb_rating"]

# These columns have TEXT affinity (seeded all-NULL), so reads come back as strings.
def _coerce_numeric(df):
    for col in _NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def update_game(steam_id, limit=5):
    engine = _default_engine()

    df = check_in_db(steam_id)
    if df is None:
        return None
    df = df.drop_duplicates(subset=['appid'])
    df = _coerce_numeric(df)

    update_sql = text("""
        UPDATE top5 SET tag1=:tag1, tag2=:tag2,
               tag3=:tag3, igdb_rating=:igdb_rating
         WHERE user_steam_id=:steam_id AND appid=:appid
    """)

    for _, row in df.iterrows():
        if pd.isna(row["igdb_rating"]):
            rating = get_rating(row["name"], int(row["appid"]))
            with engine.begin() as conn:
                conn.execute(update_sql, {
                    "tag1": row["tag1"] if not pd.isna(row["tag1"]) else None,
                    "tag2": row["tag2"] if not pd.isna(row["tag2"]) else None,
                    "tag3": row["tag3"] if not pd.isna(row["tag3"]) else None,
                    "igdb_rating": rating,
                    "steam_id": steam_id,
                    "appid": int(row["appid"]),
                })

    df = _coerce_numeric(check_in_db(steam_id))

    trailer_sql = text("""
        UPDATE top5 SET trailer=:trailer
         WHERE user_steam_id=:steam_id AND appid=:appid
    """)

    df_sorted = df.sort_values("igdb_rating", ascending=False, na_position="last")
    top = df_sorted.head(limit) 
    for _, row in top.iterrows():
        # Check if tag1 is empty. If it is, we need to fetch tags.
        if pd.isna(row["tag1"]):
            t1, t2, t3 = get_game_tags(int(row["appid"]))
            with engine.begin() as conn:
                conn.execute(update_sql, {
                    "tag1": t1,
                    "tag2": t2,
                    "tag3": t3,
                    "igdb_rating": row["igdb_rating"] if not pd.isna(row["igdb_rating"]) else None,
                    "steam_id": steam_id,
                    "appid": int(row["appid"]),
                })
        if pd.isna(row["trailer"]):
            url = get_trailer_url(row["name"])
            if url:
                with engine.begin() as conn:
                    conn.execute(trailer_sql, {
                        "trailer": url,
                        "steam_id": steam_id,
                        "appid": int(row["appid"]),
                    })

    df = _coerce_numeric(check_in_db(steam_id))
    return df.sort_values("igdb_rating", ascending=False, na_position="last")

def aggregate_tags(steam_id: str) -> list:
    """Reads the database and returns the top 3 most common tags for the user."""
    df = check_in_db(steam_id)
    
    if df is None or df.empty:
        return []
        
    tag_counter = Counter()
    
    # Loop through the dataframe and tally up tag1, tag2, and tag3
    for _, row in df.iterrows():
        for tag_col in ["tag1", "tag2", "tag3"]:
            tag_value = row[tag_col]
            # ONLY tally if the tag is NOT None and NOT empty
            if pd.notna(tag_value) and tag_value is not None:
                tag_counter[tag_value] += 1
                
    # Get the 3 most common tags (e.g., [('12:genres', 4), ('18:themes', 3), ('1:themes', 2)])
    top_3_tuples = tag_counter.most_common(3)
    
    # We just want the string tags, not the counts, so we extract them
    return [item[0] for item in top_3_tuples]