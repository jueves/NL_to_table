import os
import pymongo
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Setup Mongo
MONGO_SERVER = os.environ.get("MONGO_SERVER")
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
DATA_FILENAME = "user_data/data.csv"
DB_NAME = "testingDB"
COLLECTION_NAME = "personal"

client = pymongo.MongoClient("mongodb://" + MONGO_SERVER + ":27017",
                             username=MONGO_USER,
                             password=MONGO_PASSWORD)

db = client[DB_NAME]

collection = db[COLLECTION_NAME]

# Read data
pandas_df = pd.read_csv(DATA_FILENAME, parse_dates=["time"])

if (len(pandas_df) > 0):
    # Convert data
    if 'Unnamed: 0' in pandas_df.columns:
        pandas_df = pandas_df.drop(columns=['Unnamed: 0'])
    data_premongo = [value.dropna().to_dict() for key, value in pandas_df.iterrows()]

    # Push data to Mongo
    collection.insert_many(data_premongo)


# Test retrieving data
document = collection.find_one({"weight": 40.0})

print("### DOCUMENT RETRIVAL TEST ###")
print("Document with weight = 40.0:\n", document)
