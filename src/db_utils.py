import os
import pymongo
from bson.objectid import ObjectId
from datetime import datetime
import re

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

    def find_one(self, collection, user_id, query={}, sort=[('_id', -1)], projection=None, skip=0):
        '''
        pymongo find_one method, forcing filtering by user_id
        '''
        query['user_id'] = user_id
        answer = self._db[collection].find_one(query, sort=sort, projection=projection, skip=skip)
        return(answer)
    
    def find(self, collection, user_id, query={}, sort=[('_id', -1)], projection=None):
        '''
        pymongo find method, forcing filtering by user_id
        '''
        query['user_id'] = user_id
        answer = self._db[collection].find(query, sort=sort, projection=projection)
        return(answer)
    
    def count_documents(self, collection, user_id):
        '''
        pymongo count_documents method, forcing filtering by user_id
        '''
        count = self._db[collection].count_documents({"user_id":user_id})
        return(count)
    
    def delete_one(self, collection, user_id, query):
        '''
        pymongo delete_one method, forcing filtering by user_id
        '''
        query['user_id'] = user_id
        answer = self._db[collection].delete_one(query)
        return(answer)
    
    def delete_many(self, collection, user_id, query):
        '''
        pymongo delete_many method, forcing filtering by user_id
        '''
        query['user_id'] = user_id
        answer = self._db[collection].delete_many(query)
        return(answer)
        
    
    def update_user_field(self, user_id, field, value):
        '''
        Allows to update every field for a user except for the 'user_id' field.
        '''
        if field != "user_id":
            self._db["users"].update_many({ "user_id": user_id },
                                        { "$set": { field: value }})

    def admin_del_request(self, message):
        '''
        Gets a Telegram message object and logs it to a deletion requests file.
        '''
        request_date = datetime.utcfromtimestamp(message.date)
        request_text = " ".join(message.text.split()[1:]) # Excludes command from the text
        self.insert_one(collection="delrequests", user_id=message.from_user.id,
                        records={"date": request_date, "text": request_text})
        return(request_text)
    
    def delete_using_call(self, call):
        '''
        Deletes record from "personal" collection in the database.
        Gets the id of the record to be deleted from the end of the message text
        in the call.
        '''
        user_id = call.from_user.id
        message_text = call.message.text
        record_id_str = re.findall(r"Record_id:\s([0-9a-fA-F]+)", message_text)[-1]
        record_id = ObjectId(record_id_str)
        self.delete_one("personal", user_id, {"_id": record_id})

    def unload_user_examples(self, user_id):
        '''
        Deletes user_id's example data.
        Returns the amount of deleted documents.
        Raise error if transaction not acknowledged.
        '''
        query = {"isexample":True}
        delete_result = self.delete_many("personal", user_id, query)
        if not delete_result.acknowledged:
            raise ValueError(f'Delete many operation not acknowledged.\n'
                             f'{delete_result.deleted_count} records where deleted.')
        return(delete_result.deleted_count)
