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
    
    def user_exists(self, user_id):
        '''
        Gets user_id
        Returns True or False depending on user existence
        '''
        if user_id in self.users_list:
            exists = True
        elif self._db["users"].count_documents({"user_id":user_id}) > 0:
            exists = True
            self.users_list.append(user_id)
        else:
            exists = False
        return(exists)
    
    def add_user(self, user_id):
        '''
        Gets new user_id
        Adds new user
        '''
        # Set data structure
        if self._db["users"].count_documents({"user_id":user_id}) == 0:
            # Set data structure
            default_doc = self._db["users"].find_one({"user_id":0})
            newuser_doc = {"user_id":user_id,
                           "data_structure":default_doc["data_structure"],
                           "prompt_header":self.get_prompt_header(default_doc["data_structure"],
                                                                  default_doc["prompt_raw"])}
            self._db["users"].insert_one(newuser_doc)
        else:
            raise RuntimeError("The user already exists.")

        # Create initial last use document
        if self._db["lastuse"].count_documents({"user_id":user_id}) == 0:
            # Create the initial lastuse document
            lastuse_dict = {}
            data_structure = self._db["users"].find_one({"user_id": user_id})["data_structure"]
            for variable in  data_structure.keys():
                lastuse_dict[variable] = datetime.strptime("2023-01-01", "%Y-%m-%d")
            lastuse_dict["time"] = datetime.now()
            lastuse_dict["user_id"] = user_id
            self._db["lastuse"].insert_one(lastuse_dict)
        else:
            raise RuntimeError("lastuse has already been initiated for this user.")
        
    def update_user(self, user_id, data_structure):
        '''
        Updates user's data_structure and prompt
        '''

    
    def get_prompt_header(self, data_structure, prompt_raw):
        '''
        Generates a prompt based on the defined data structure to set how
        chatGPT should behave.
        '''
        # Generate variable description
        var_description = ""
        for var_name, var_metadata in data_structure.items():
            var_description += "{name}, {description}\n".format(name=var_name,
                                                                description=var_metadata["description"])

        # Generate example data
        example_dic = {}
        for var_name in data_structure.keys():
            example_dic[var_name] = data_structure[var_name]["example"]
        example_csv = pd.DataFrame.from_dict(example_dic).to_csv(index=False)
        prompt_header = prompt_raw.format(description=var_description, example=example_csv)
        return(prompt_header)
    
    '''
    def load_example_data(self, user_id, file_name):
        # Loads example dummy data on database for user_id.
        try:
            data = pd.read_csv(file_name, parse_dates=["time"])
            lastuse = {}
            for var_name in data.columns:
                lastuse[var_name] = datetime.now()
            lastuse["user_id"] = user_id
            data["user_id"] = user_id

            self.db.personal.insert_many(data.to_dict(orient="records"))
            self.db.lastuse.insert_one(lastuse)
            answer = "Datos cargados."
        except Exception as e:
            answer = f"<b>Algo ha salido mal:</b>\n{e}"
        return(answer)
    '''
        