from io import StringIO
import os
import json
from datetime import datetime
import pandas as pd
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
import whisper
from sanity_check import sanity_check

DATA_FILENAME = "user_data/data.csv"
telegram_key = os.environ.get("TELEGRAM_KEY")
chatGPT_key = os.environ.get("CHATGPT_KEY")
telegram_user_id = os.environ.get("TELEGRAM_USER_ID")

# Load text messages
with open("data_structure.json", "r", encoding="utf-8") as f:
    data_structure = json.load(f)



def get_prompt_header(file_A1="prompt_A1.txt", file_A2="prompt_A2.txt", file_B1="prompt_B1.txt", data_structure=data_structure):
    # Load fixed texts
    with open(file_A1, "r", encoding="utf-8") as f:
        prompt_A1 = f.read()

    with open(file_A2, "r", encoding="utf-8") as f:
        prompt_A2 = f.read()

    with open(file_B1, "r", encoding="utf-8") as f:
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
    print("PROMPT HEADER\n" + prompt_header)
    return(prompt_header)

def get_prompt(text, message_date):
    message_time = datetime.utcfromtimestamp(message_date)
    timestr = message_time.strftime("%d.%m.%Y %H:%M:%S, ")
    prompt = "Current time is " + timestr + text
    return(prompt)

def text_to_csv(text, message_date):
    '''
    Takes telebot metada whose text describes a table and converts
    it to csv using chatGPT.
    The prompt sent to GPT includes a fixed header describing the table structure.
    '''
    txt_input = get_prompt(text, message_date)
    messages = [ {"role": "system", "content": get_prompt_header()} ]
    messages.append({"role": "user", "content": txt_input})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    
    reply = chat.choices[0].message.content
    return(reply)

def gen_markup(add_buttons=False):
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

def update_dataset(data_filename=DATA_FILENAME):
    '''
    Takes the names of the whole dataset file and the new data file.
    Performs an update attaching all new data to the whole dataset.
    Writes changes to disk.
    '''
    data = pd.read_csv(data_filename)
    new_data = pd.read_csv("user_data/" + str(telegram_user_id) + "_tmp.csv")
    data = pd.concat([data, new_data], ignore_index=True)
    data = data[list(data_structure.keys())]
    data.to_csv(data_filename)

def get_table(text, time, user_id):
    '''
    Gets a message whose text describes data values, transforms, checks and
    saves the data.
    Returns answer text with information about the process.
    '''
    csv_data = text_to_csv(text, time)
    new_data = pd.read_csv(StringIO(csv_data))
    new_data.to_csv("user_data/" + str(user_id) + "_tmp.csv")
    data, answer = sanity_check(new_data)
    answer = data.T.to_markdown() + answer
    return(answer)

