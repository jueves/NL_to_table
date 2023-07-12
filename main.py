from io import StringIO
import json
from datetime import datetime
import pandas as pd
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
import whisper
from sanity_check import sanity_check

DATA_FILENAME = "data.csv"

# Load keys
with open("keys.json", "r", encoding="utf-8") as f:
    keys_dic = json.load(f)

# Load text messages
with open("prompt_header.txt", "r", encoding="utf-8") as f:
    prompt_header = f.read()

with open("data_structure.json", "r", encoding="utf-8") as f:
    data_structure = json.load(f)

with open("start.txt", "r", encoding="utf-8") as f:
    start_message = f.read()

with open("help.txt", "r", encoding="utf-8") as f:
    help_message = f.read()

def just_chat(text):
    '''
    Takes a string with a message to chatGPT and returns the answer.
    '''
    messages.append({"role": "user", "content": text})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    
    reply = chat.choices[0].message.content
    return(reply)

def message_to_csv(message):
    '''
    Takes a telebot message object whose text describes a table and converts
    it to csv using chatGPT.
    The prompt sent to GPT includes a fixed header describing the table structure.
    '''
    message_time = datetime.utcfromtimestamp(message.date)
    timestr = message_time.strftime("%d.%m.%Y %H:%M:%S  ")
    txt_input = prompt_header + timestr + message.text

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
    user_id = keys_dic["telegram_user_id"]
    data = pd.read_csv(data_filename)
    new_data = pd.read_csv(str(user_id) + "_tmp.csv")
    data = pd.concat([data, new_data], ignore_index=True)
    data = data[list(data_structure.keys())]
    data.to_csv(data_filename)

def get_table(message):
    '''
    Gets a message whose text describes data values, transforms, checks and
    saves the data.
    Returns answer text with information about the process.
    '''
    csv_data = message_to_csv(message)
    new_data = pd.read_csv(StringIO(csv_data))
    new_data.to_csv(str(message.from_user.id) + "_tmp.csv")
    data, answer = sanity_check(new_data)
    answer = data.T.to_markdown() + answer
    return(answer)

# Setup chatGPT
openai.api_key = keys_dic["chatGPT"]
messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]

# Setup Whisper
whisper_model = whisper.load_model("base")

# Setup Telegram bot
bot = telebot.TeleBot(keys_dic["telegram"])

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    '''
    Manages callback for data validation buttons
    '''
    if call.data == "cb_correct":
        user_id = keys_dic["telegram_user_id"]
        if (str(call.from_user.id) == user_id):
            # Only saves data for user_id
            update_dataset(DATA_FILENAME)
            bot.answer_callback_query(call.id, "Datos guardados.")

        else:
            bot.answer_callback_query(call.id, "Has confirmado la tabla propuesta.")
    
    elif call.data == "cb_errors":
        bot.answer_callback_query(call.id, "Has marcado la tabla propuesta como erronea.")

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('voice_note.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    result = whisper_model.transcribe("voice_note.ogg")
    bot.reply_to(message, result["text"])


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    '''
    Takes all incoming messages and returns answers.
    '''
    add_buttons = False
    if (message.text == "/start"):
        answer = start_message + help_message
    elif (message.text == "/help"):
        answer = help_message
    elif (message.text == "/metadata"):
        answer = json.dumps(data_structure, indent=4)
    elif (message.text[:5] == "/chat" or message.text[:2] == ". "):
        answer = just_chat(message.text[6:])
    elif (message.text == "/hora"):
        answer = str(datetime.now())
    else:
        add_buttons = True
        answer = get_table(message)

    bot.send_message(message.chat.id, answer, reply_markup=gen_markup(add_buttons))

bot.infinity_polling()
