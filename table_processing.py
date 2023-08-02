from io import StringIO
from datetime import datetime
import pandas as pd
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
from sanity_check import sanity_check


class Text2Table:
    def __init__(self, data_structure, filenames_dic, telegram_user_id, data_filename):
        self.data_structure = data_structure
        self.telegram_user_id = telegram_user_id
        self.data_filename = data_filename
        self.tmp_data = {}
        self.prompt_header = self.get_prompt_header(data_structure, filenames_dic)

    def get_prompt_header(self, data_structure, filenames_dic):
        '''
        Generates a prompt based on the defined data structure to set how
        chatGPT should behave.
        '''
        # Load fixed texts
        with open(filenames_dic["A1"], "r", encoding="utf-8") as f:
            prompt_A1 = f.read()

        with open(filenames_dic["A2"], "r", encoding="utf-8") as f:
            prompt_A2 = f.read()

        with open(filenames_dic["B1"], "r", encoding="utf-8") as f:
            prompt_B1 = f.read()

        # Generate variable description
        var_description = ""
        for var_name, var_metadata in data_structure.items():
            var_description += "{name}, {description}\n".format(name=var_name, description=var_metadata["description"])

        # Generate example data
        example_dic = {}
        for var_name in data_structure.keys():
            example_dic[var_name] = data_structure[var_name]["example"]
        example_csv = pd.DataFrame.from_dict(example_dic).to_csv(index=False)
        prompt_header = prompt_A1 + var_description + prompt_A2 + example_csv + prompt_B1
        return(prompt_header)

    def text_to_csv(self, text, message_date):
        '''
        Takes telebot metada whose text describes a table and converts
        it to csv using chatGPT.
        The prompt sent to GPT includes a fixed header describing the table structure.
        '''
        message_date = datetime.utcfromtimestamp(message_date)
        timestr = message_date.strftime("%d.%m.%Y %H:%M:%S")
        txt_input = text + "\nCurrent time is " + timestr
        messages = [ {"role": "system", "content": self.prompt_header} ]
        messages.append({"role": "user", "content": txt_input})
        chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        
        reply = chat.choices[0].message.content
        return(reply)

    def gen_markup(self, add_buttons=False):
        '''
        If add_buttons=True, it returns a telebot markup object that adds buttons
        to the message. Otherwise, it returns an empty markup.
        '''
        markup = InlineKeyboardMarkup()
        if add_buttons:
            markup.row_width = 2
            markup.add(InlineKeyboardButton("Todo correcto", callback_data="cb_correct"),
                       InlineKeyboardButton("Hay errores", callback_data="cb_errors"))
        return markup

    def update_dataset(self):
        '''
        Takes the names of the whole dataset file and the new data file.
        Performs an update attaching all new data to the whole dataset.
        Writes changes to disk.
        '''
        data = pd.read_csv(self.data_filename)
        #new_data = pd.read_csv("user_data/" + str(self.telegram_user_id) + "_tmp.csv")
        data = pd.concat([data, self.tmp_data[self.telegram_user_id]], ignore_index=True)
        data = data[list(self.data_structure.keys())]
        data.to_csv(self.data_filename)

    def get_table(self, text, time, user_id):
        '''
        Gets a message whose text describes data values, transforms, checks and
        saves the data.
        Returns answer text with information about the process.
        '''
        csv_data = self.text_to_csv(text, time)
        new_data = pd.read_csv(StringIO(csv_data))
        self.tmp_data[user_id] = new_data
        print(self.tmp_data)
        data, answer = sanity_check(new_data)
        answer = data.T.to_markdown() + answer
        return(answer)

