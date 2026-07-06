import pandas as pd
import sqlalchemy as db

#dummy/testing for rn
###testing for add to db function
gameMetadata = {
                "ID:": "000",
                "title": "example",
                "summary": "This is typically a really long summary, roughly about 2x this length if it matters",
                "publishers": "publisher",
                "price": "$0.00 USD",
                "release_date": "23 Apr, 20XX"
}



metadataDF = pd.DataFrame.from_dict([gameMetadata])
engine = db.create_engine("sqlite:///data/metadataDB.db")
metadataDF.to_sql("table_name", con=engine, if_exists = "append", index=False)

###testing for get from db function
gameID = "000"
with engine.connect() as connection:
   query_result = connection.execute(db.text("SELECT title FROM table_name WHERE id = ?;")).fetchall()
   print(pd.DataFrame(query_result))