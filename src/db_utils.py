import os
import pymongo
from datetime import datetime
import pandas as pd

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
        self._db = client[db_name]
        self.users_list = []
                
    def insert_one(self, collection, user_id, records):
        '''
        pymongo insert_one method, forcing filtering by user_id
        '''
        records["user_id"] = user_id
        self._db[collection].insert_one(records)
    
    def insert_many(self, collection, user_id, records):
        '''
        pymongo insert_many method, forcing filtering by user_id
        '''
        for document in records:
            document.update({"user_id":user_id})
        self._db[collection].insert_many(records)

    def find_one(self, collection, user_id, query={}, sort=None, projection=None):
        '''
        pymongo find_one method, forcing filtering by user_id
        '''
        query['user_id'] = user_id
        answer = self._db[collection].find_one(query, sort=sort, projection=projection)
        return(answer)
    
    def find(self, collection, user_id, query={}, sort=None, projection=None):
        '''
        pymongo find method, forcing filtering by user_id
        '''
        query['user_id'] = user_id
        answer = self._db[collection].find(query, sort=sort, projection=projection)
        return(answer)
    
    def count_documents(self, collection, user_id):
        count = self._db[collection].count_documents({"user_id":user_id})
        return(count)
    
    def del_request(self, message):
        '''
        Gets a Telegram message object and logs it to a deletion requests file.
        '''
        request_date = datetime.utcfromtimestamp(message.date)
        request_text = " ".join(message.text.split()[1:]) # Excludes command from the text
        self.insert_one(collection="delrequests", user_id=message.from_user.id,
                        records={"date": request_date, "text": request_text})
        return(request_text)