import os
import pymongo

MONGO_SERVER = "mongo"
MONGO_USER = os.environ.get("MONGO_USER")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")
DB_NAME = "main"

class MongoManagerPerUser:
    '''
    Manages Mongo connections enforcing filter by user_id.
    '''
    def __init__(self, db_name=DB_NAME, db_server=MONGO_SERVER, db_user=MONGO_USER,
                db_password=MONGO_PASSWORD):
        client = pymongo.MongoClient("mongodb://" + db_server + ":27017",
                                    username=db_user,
                                    password=db_password)
        self.db = client[db_name]
                
    def insert_one(self, collection, user_id, data_dict):
        data_dict["user_id"] = user_id
        self.db[collection].insert_one(data_dict)

    def find_one(self, collection, user_id, query, sort=['time', -1], projection={"_id":0}):
        query['user_id'] = user_id
        answer = self.db[collection].find_one(query, sort=sort, projection=projection)
        return(answer)