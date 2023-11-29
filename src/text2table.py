from io import StringIO
from datetime import datetime
import pandas as pd
import openai
from sanity_check import sanity_check

class Text2Table:
    '''
    Creates a Text2Table object that stores metadata, temporal data and performs
    various data transformations.
    '''
    def __init__(self, db):
        self.db = db
        self.tmp_data = {}
        self.messages = {}
    
    def text_to_csv(self, message):
        '''
        Takes telebot metada whose text describes a table and converts
        it to csv using chatGPT.
        The prompt sent to GPT includes a fixed header describing the table structure.
        '''
        user_dict = self.db.find_one(collection="users", user_id=message.from_user.id)
        prompt_header = user_dict["prompt_header"]
        message_date = datetime.utcfromtimestamp(message.date)
        timestr = message_date.strftime("%Y-%m-%d %H:%M:%S")
        txt_input = message.text + "\nCurrent time is " + timestr
        self.messages[message.from_user.id] = [ {"role": "system", "content": prompt_header} ]
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
            new_csv
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
        if len(critique) == 0:
            critique = sanity_check(self.tmp_data[user_id])
        messages = self.messages[user_id]
        messages.append({"role": "user", "content": '''Esa tabla contiene errores. {critique}.
                          Respóndeme únicamente con la tabla corregida, sin incluir
                          ningún otro texto antes o despues.'''.format(critique=critique)
                         })
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        new_csv = chat.choices[0].message.content
        return(new_csv)

    def update_dataset(self, user_id, filename=""):
        '''
        Updates database with new data.
        '''    
        if len(filename)==0:
            dataframe = self.tmp_data[user_id].dropna(axis=1)
        else:
            dataframe = pd.read_csv(filename, parse_dates=["time"])
       
        # Update lastuse collection
        self.add_to_lastuse(user_id, dataframe)
        
        # Write changes to database
        records = dataframe.to_dict(orient="records")
        if len(records) == 1:
            self.db.insert_one("personal", user_id, records[0])
        else:
            self.db.insert_many("personal", user_id, records)

    def del_request(self, message):
        '''
        Gets a Telegram message object and logs it to a deletion requests file.
        '''
        request_date = datetime.utcfromtimestamp(message.date)
        request_text = message.text[4:] # Excludes text begginig: "/del"
        self.db.insert_one(collection="delrequests", user_id=message.from_user.id,
                           records={"date": request_date, "text": request_text})

    def add_to_lastuse(self, user_id, dataframe):
        '''
        Gets a dictionary with the new data collected.
        Updates lastuse Mongo collection with the date each
        variable was recorded for the last time.
        '''
        # Get last log in lastuse collection
        lastuse = self.db.find_one(collection="lastuse", user_id=user_id,
                                   sort=[('time', -1)], projection={"_id":0})
        
        # Get lastuse_time
        if len(dataframe) == 1:
            lastuse_time = dataframe["time"][0]
        else:
            # For simplicity, if multiple observations are being loaded at once,
            # we set current datetime as lastuse datetime.
            # Currently (v0.9.2) only dummy data is loaded in bulk.
            lastuse_time = datetime.now()

        # Set new time
        for var_name in dataframe.columns:
            if lastuse[var_name] < lastuse_time:
                lastuse[var_name] = lastuse_time
        lastuse["isexample"] = "isexample" in dataframe.columns
        lastuse["time"] = datetime.now()

        # Insert data        
        self.db.insert_one(collection="lastuse", user_id=user_id,
                           records=lastuse)
