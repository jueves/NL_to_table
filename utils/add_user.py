# First versions of the project where single use only.
# This adds a user to old MongoDB documents making them compatible
# with the multiuser version.
# In order to modify production database, expose port 27017 on
# the mongo service and use the proper .env file.
import json
import os
import pymongo
from dotenv import load_dotenv
from datetime import datetime, timedelta
from icecream import ic

# Load keys
load_dotenv()
MONGO_SERVER = "mongo"
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
TELEGRAM_USER_ID = int(os.environ.get("TELEGRAM_USER_ID"))
DUMMY_USER_ID = 12345
DB_NAME = "main"
INSERT_OLD_DATA = False

# Setup Mongo Connection
client = pymongo.MongoClient("mongodb://" + MONGO_SERVER + ":27017",
                             username=MONGO_USER, password=MONGO_PASSWORD)
db = client[DB_NAME]

# Write old data (data without user) to MongoDB for testing purpouses
with open("config/data_structure.json", "r") as f:
    data_structure = json.load(f)

def insert_old_data(db, data_structure):
    # Add to lastuse
    for i in range(1,5):
        dummy_data = {}
        date = datetime.now() - timedelta(i)
        for key in data_structure.keys():
            dummy_data[key] = date
        db.lastuse.insert_one(dummy_data)

if INSERT_OLD_DATA:
    insert_old_data(db, data_structure)
    print("### Data without user_id inserted.")

ic(db.lastuse.find_one({ "user_id": { "$exists": False } }))
ic(db.lastuse.find_one({ "user_id": { "$exists": True } }))
ic(db.lastuse.find_one({ "user_id": DUMMY_USER_ID }))
ic(db.lastuse.find_one({ "user_id": TELEGRAM_USER_ID }))

# Add user to old data
def add_user(db, user_id, collections_list):
    for collection in collections_list:
        db[collection].update_many({ "user_id": { "$exists": False } },
                                   { "$set": { "user_id": user_id }})

def replace_user(db, old_user_id, new_user_id, collections_list):
    for collection in collections_list:
        db[collection].update_many({ "user_id": old_user_id },
                                   { "$set": { "user_id": new_user_id }})

add_user(db, TELEGRAM_USER_ID, ["lastuse", "delrequests", "personal"])
print("### User added to all data without user.")

ic(db.lastuse.find_one({ "user_id": { "$exists": False } }))
ic(db.lastuse.find_one({ "user_id": { "$exists": True } }))
ic(db.lastuse.find_one({ "user_id": DUMMY_USER_ID }))
ic(db.lastuse.find_one({ "user_id": TELEGRAM_USER_ID }))


print("### Replace DUMMY_USER_ID with TELEGRAM_USER_ID:")
replace_user(db, DUMMY_USER_ID, TELEGRAM_USER_ID, ["lastuse", "delrequests", "personal"])
ic(db.lastuse.find_one({ "user_id": DUMMY_USER_ID }))
ic(db.lastuse.find_one({ "user_id": TELEGRAM_USER_ID }))
