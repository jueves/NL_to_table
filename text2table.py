from io import StringIO
from datetime import datetime
import pandas as pd
import openai
import json
from sanity_check import sanity_check
from db_utils import get_mongo_collection

class Text2Table:
    '''
    Creates a Text2Table object that stores metadata, temporal data and performs
    various data transformations.
    '''
    def __init__(self, data_structure, prompt_raw, telegram_user_id):
        self.data_structure = data_structure
        self.telegram_user_id = int(telegram_user_id)
        self.collection = get_mongo_collection()
        self.tmp_data = {}
        self.messages = {}
        self.prompt_header = self.get_prompt_header(data_structure, prompt_raw)
    
    def get_prompt_header(self, data_structure, prompt_raw):
        '''
        Generates a prompt based on the defined data structure to set how
        chatGPT should behave.
        '''

        # Generate variable description
        var_description = ""
        for var_name, var_metadata in data_structure.items():
            var_description += "{name}, {description}\n".format(name=var_name, description=var_metadata["description"])

        # Generate example data
        example_dic = {}
        for var_name in data_structure.keys():
            example_dic[var_name] = data_structure[var_name]["example"]
        example_csv = pd.DataFrame.from_dict(example_dic).to_csv(index=False)
        prompt_header = prompt_raw.format(description=var_description, example=example_csv)
        return(prompt_header)

    def text_to_csv(self, message):
        '''
        Takes telebot metada whose text describes a table and converts
        it to csv using chatGPT.
        The prompt sent to GPT includes a fixed header describing the table structure.
        '''
        message_date = datetime.utcfromtimestamp(message.date)
        timestr = message_date.strftime("%Y-%m-%d %H:%M:%S")
        txt_input = message.text + "\nCurrent time is " + timestr
        self.messages[message.from_user.id] = [ {"role": "system", "content": self.prompt_header} ]
        self.messages[message.from_user.id].append({"role": "user", "content": txt_input})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages[message.from_user.id])
        
        reply = chat.choices[0].message.content
        return(reply)

    def csv2answer(self, csv_data, user_id):
        '''
        Gets a string of csv data and a user id.
        Converts string to dataframe
        Performs sanity check
        Returns answer
        '''
        new_data = pd.read_csv(StringIO(csv_data))

        i = 0
        while not "time" in new_data.columns and i < 4:
            i =+ 1
            print("ERROR: time missing, asking for correction.")
            new_csv = self.get_correction(user_id, critique="No has incluído la columna time.")
            new_data = pd.read_csv(StringIO(new_csv))
        
        new_data["time"] = pd.to_datetime(new_data.time, format="mixed", dayfirst=True)

        self.tmp_data[user_id] = new_data
        answer = self.df_to_markdown(new_data) + sanity_check(new_data)
        return(answer)                        

    def df_to_markdown(self, new_data):
        '''
        Gets a new_data Pandas DataFrame and returns it as a Sring in a clear
        Markdown structure.
        '''
        new_data = new_data.dropna(axis=1)
        date_time = new_data.time
        new_data = new_data.drop(columns=["time"])
        new_data["date"] = date_time.map(datetime.date)
        new_data["time"] = date_time.map(datetime.time)
        new_data_md = new_data.T.to_markdown()
        return(new_data_md)

    def get_table(self, message):
        '''
        Gets a message whose text describes data values, transforms, checks and
        saves the data.
        Returns answer text with information about the process.
        '''
        csv_str = self.text_to_csv(message)
        answer = self.csv2answer(csv_str,
                                 message.from_user.id)
        return(answer)

    def get_correction(self, user_id, critique=""):
        '''
        Returns csv correction for the last message sent to chatGPT.
        '''
        messages = self.messages[user_id]
        messages.append({"role": "user", "content": "Esa tabla contiene errores. {critique}" + 
                         " Respóndeme únicamente con la tabla corregida, sin incluir" +
                          "ningún otro texto antes o despues.".format(critique=critique)
                         })
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        new_csv = chat.choices[0].message.content
        return(new_csv)

    def update_dataset(self):
        '''
        Updates database with new data.
        '''
        # Convert data      
        data_short = self.tmp_data[self.telegram_user_id].dropna(axis=1)
        data_dict = data_short.to_dict(orient='records')[0]
        
        # Write changes to database
        self.collection.insert_one(data_dict)
        
        # Test retrieving data
        self.collection.find_one({"weight": 40.0})

    def del_request(self, message):
        '''
        Gets a Telegram message object and logs it to a deletion requests file.
        '''
        try:
            with open("user_data/deletion_requests.json", "r") as f:
               requests = json.load(f)
        except:
            requests = {}
        message_date = datetime.utcfromtimestamp(message.date)
        request_date = message_date.strftime("%Y-%m-%d %H:%M:%S")
        requests[request_date] = message.text[4:]
        with open("user_data/deletion_requests.json", "w") as f:
            json.dump(requests, f, indent=4)
