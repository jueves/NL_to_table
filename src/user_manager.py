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
            with open("config/data_structure.json", "r", encoding="utf-8") as f:
                data_structure = json.load(f)
            with open("text/prompt.txt", "r", encoding="utf-8") as f:
                prompt_raw = f.read()
            # Set data structure
            newuser_doc = {"user_id":user_id,
                           "data_structure":data_structure,
                           "prompt_header":self.get_prompt_header(data_structure,
                                                                  prompt_raw),
                           "whisper_prompt":self.get_whisper_prompt(data_structure)
                           }
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
      '''
      Sends user a copy of its own data structure json file.
      '''
      filename = f"user_data/{message.from_user.id}_data_structure.json"
      with open(filename, "w") as json_file:
          data_structure = self.db.find_one("users", message.from_user.id)["data_structure"]
          json.dump(data_structure, json_file, indent=4)
      with open(filename, "r") as json_file:
          self.bot.send_document(message.chat.id, reply_to_message_id=message.message_id,
                               document=json_file)
     
    def set_data_structure(self, user_id, data_structure_filename):
        '''
        Sets new data_structure in database for user_id.
        '''
        sanity_report = validate_data_structure(data_structure_filename)
        if sanity_report == "no errors":
            try:
                with open(data_structure_filename, "r") as f:
                    data_structure = json.load(f)
                whisper_prompt = self.get_whisper_prompt(data_structure)
                self.db.update_user_field(user_id, "data_structure", data_structure)
                self.db.update_user_field(user_id, "whisper_prompt", whisper_prompt)
                answer = "Se ha cargado la configuración"
            except Exception as e:
                answer = f"Error: Los datos no pudieron ser cargados.\n{e}"
        else:
            answer = sanity_report
        return(answer)
    
    def get_whisper_prompt(self, data_structure):
        '''
        Takes data structure.
        Returns a string of example data inputs for primming Whisper.
        Output structure: "var1_name, var1_value. var2_name, var2_value."
        '''
        examples=4   # If set to 0 only variable names are returned.
        whisper_prompt_list = []
        if examples == 0:
            for key, value in data_structure.items():
                if key != "time":
                    if "alias" in value.keys():
                        key_name = value["alias"]
                    else:
                        key_name = key
                    whisper_prompt_list.append(key_name)
        else:
            # In order to obtain a better order, iterate first on range, then on dict.
            # Otherwise all examples of the same variable are next to each other, producing
            # poor Whisper transcriptions.
            for example_number in range(examples):
                for key, value in data_structure.items():
                    if key != "time":
                        if "alias" in value.keys():
                            key_name = value["alias"]
                        else:
                            key_name = key
                        try:
                            key_and_value = key_name + f', {value["example"][example_number]}'
                            whisper_prompt_list.append(key_and_value)
                        except IndexError:
                            print(f"Index Error: The variable \"{key}\" doesn't have an"
                                   f" example with index {example_number}.", flush=True)

        whisper_prompt = ". ".join(whisper_prompt_list)
        return(whisper_prompt)
