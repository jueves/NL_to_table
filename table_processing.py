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
    def __init__(self, data_structure, prompt_filename, telegram_user_id, data_filename):
        self.data_structure = data_structure
        self.telegram_user_id = int(telegram_user_id)
        self.data_filename = data_filename
        self.tmp_data = {}
        self.messages = {}
        self.prompt_header = self.get_prompt_header(data_structure, prompt_filename)
    
    def get_prompt_header(self, data_structure, prompt_filename):
        '''
        Generates a prompt based on the defined data structure to set how
        chatGPT should behave.
        '''
        with open(prompt_filename, "r", encoding="utf-8") as f:
            prompt_raw = f.read()

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
        timestr = message_date.strftime("%d.%m.%Y %H:%M:%S")
        txt_input = message.text + "\nCurrent time is " + timestr
        self.messages[message.from_user.id] = [ {"role": "system", "content": self.prompt_header} ]
        self.messages[message.from_user.id].append({"role": "user", "content": txt_input})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=self.messages[message.from_user.id])
        
        reply = chat.choices[0].message.content
        return(reply)

    def update_dataset(self):
        '''
        Takes the names of the whole dataset file and the new data file.
        Performs an update attaching all new data to the whole dataset.
        Writes changes to disk.
        '''
        # Add new data
        data = pd.read_csv(self.data_filename, parse_dates=["time"])
        data = pd.concat([data, self.tmp_data[self.telegram_user_id]], ignore_index=True)

        # Filter out variables not in data structure
        data = data[list(self.data_structure.keys())]
        
        # Write changes to disk
        data.to_csv(self.data_filename)

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

    def csv2answer(self, csv_data, user_id):
        '''
        Gets a string of csv data and a user id.
        Converts string to dataframe
        Performs sanity check
        Returns answer
        '''
        new_data = pd.read_csv(StringIO(csv_data))
        new_data["time"] = pd.to_datetime(new_data.time, format="mixed", dayfirst=True)
        self.tmp_data[user_id] = new_data
        answer = sanity_check(new_data)
        new_data = new_data.dropna(axis=1)
        answer = new_data.T.to_markdown() + answer
        return(answer)                        

    def get_correction(self, user_id):
        '''
        Returns csv correction for the last message sent to chatGPT.
        '''
        messages = self.messages[user_id]
        messages.append({"role": "user", "content": "Esa tabla contiene errores." + 
                         " Respóndeme únicamente con la tabla corregida, sin incluir" +
                          "ningún otro texto antes o despues."
                         })
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        new_csv = chat.choices[0].message.content
        return(new_csv)


class Reminders:
    '''
    Calculates unuse score.
    '''
    def __init__(self, data_filename, metadata):
        self.data = pd.read_csv(data_filename, parse_dates=["time"])
        self.metadata = metadata

    def get_score(self, var_name):
        '''
        Returns a score representing how unused is the variable.
        The default metric is "number of days withot loggind new data."
        '''
        subdata = self.data[[var_name, "time"]].dropna()
        try:
            subdata = subdata.sort_values("time")
            last_date = subdata.time.iloc[-1]
            score = datetime.now() - last_date
        except:
            score = pd.Timedelta(days=1000)
<<<<<<< HEAD
        score = score.days
=======
            
>>>>>>> refs/remotes/origin/main
        return(score)


    def get_score_df(self):
        '''
        Returns the last use score for every variable.
        '''
        var_names = []
        scores = []
        for var_name in self.metadata.keys():
            if var_name != "time":
                var_names.append(var_name)
                scores.append(self.get_score(var_name))
<<<<<<< HEAD
        score_df = pd.DataFrame({"var_name":var_names, "score":scores}).sort_values("score",ascending=False)
=======
        score_df = pd.DataFrame({"var_name":var_names, "score":scores})
        score_df = score_df.sort_values("score", ascending=False)
>>>>>>> refs/remotes/origin/main
        return(score_df)

    def get_reminders(self):
       ''' Gets dataset(pd.DataFrame)
          Returns advice(str)
       '''
       last_log = self.get_score_df()
       advice = "Hace {days} días que no registras {var}, ¿añades una observación?".format(days=last_log.score[0],
                                                                                           var=last_log.var_name[0])
       return(advice)

