from datetime import datetime
import pandas as pd
import json
from sanity_check import validate_data_structure

class UserManager:
    '''
    Manages users and its metadata.
    '''
    def __init__(self, db, bot):
        '''
        Gets an object of the class MongoManagerPerUser, and
        a Telebot object.
        '''
        self.db = db
        self.bot = bot
        self.users_list = []

    def user_exists(self, user_id):
        '''
        Gets user_id
        Returns True or False depending on user existence
        '''
        if user_id in self.users_list:
            exists = True
        elif self.db.count_documents("users", user_id) > 0:
            exists = True
            self.users_list.append(user_id)
        else:
            exists = False
        return(exists)
    
    def add_user(self, user_id):
        '''
        Gets new user_id
        Adds new user to database
        '''
        # Set data structure
        if self.db.count_documents("users", user_id) == 0:
            # Set data structure
            default_doc = self.db.find_one(collection="users", user_id=0)
            newuser_doc = {"user_id":user_id,
                           "data_structure":default_doc["data_structure"],
                           "prompt_header":self.get_prompt_header(default_doc["data_structure"],
                                                                  default_doc["prompt_raw"])}
            self.db.insert_one("users", user_id, newuser_doc)
        else:
            raise RuntimeError("The user already exists.")

        # Create initial last use document
        if self.db.count_documents("lastuse", user_id) == 0:
            # Create the initial lastuse document
            lastuse_dict = {}
            data_structure = self.db.find_one("users", user_id)["data_structure"]
            for variable in  data_structure.keys():
                lastuse_dict[variable] = datetime.strptime("2023-01-01", "%Y-%m-%d")
            lastuse_dict["time"] = datetime.now()
            self.db.insert_one("lastuse", user_id, lastuse_dict)
        else:
            raise RuntimeError("lastuse has already been initiated for this user.")
            
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

    def send_data_structure(self, message):
      filename = f"user_data/{message.from_user.id}_data_structure.json"
      with open(filename, "w") as json_file:
          data_structure = self.db.find_one("users", message.from_user.id)["data_structure"]
          json.dump(data_structure, json_file, indent=4)
      with open(filename, "r") as json_file:
          self.bot.send_document(message.chat.id, reply_to_message_id=message.message_id,
                               document=json_file)
     
    def set_data_structure(self, user_id, data_structure_filename):
       validation_report = validate_data_structure(data_structure_filename)
       return(validation_report)

   
        