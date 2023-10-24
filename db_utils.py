import os
import pymongo

MONGO_SERVER = "mongo"
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
DB_NAME = "main"
COLLECTION_NAME = "personal"

def get_mongo_collection(db_server=MONGO_SERVER, db_user=MONGO_USER, db_password=MONGO_PASSWORD,
                   db_name=DB_NAME, collection_name=COLLECTION_NAME):
    client = pymongo.MongoClient("mongodb://" + db_server + ":27017",
                                username=db_user,
                                password=db_password)
    db = client[db_name]
    collection = db[collection_name]
    return(collection)
