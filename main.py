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
from table_processing import get_table, update_dataset, gen_markup

# Set constants
DATA_FILENAME = "user_data/data.csv"
telegram_key = os.environ.get("TELEGRAM_KEY")
chatGPT_key = os.environ.get("CHATGPT_KEY")
telegram_user_id = os.environ.get("TELEGRAM_USER_ID")

# Load text messages
with open("data_structure.json", "r", encoding="utf-8") as f:
    data_structure = json.load(f)

with open("text/start.txt", "r", encoding="utf-8") as f:
    start_message = f.read()

with open("text/help.txt", "r", encoding="utf-8") as f:
    help_message = f.read()


# Setup chatGPT
openai.api_key = chatGPT_key

# Setup Whisper
whisper_model = whisper.load_model("tiny")

# Setup Telegram bot
bot = telebot.TeleBot(telegram_key)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    '''
    Manages callback for data validation buttons
    '''
    if call.data == "cb_correct":
        if (str(call.from_user.id) == telegram_user_id):
            # Only saves data for user_id
            update_dataset(DATA_FILENAME)
            bot.answer_callback_query(call.id, "Datos guardados.")

        else:
            bot.answer_callback_query(call.id, "Has confirmado la tabla propuesta.")
    
    elif call.data == "cb_errors":
        bot.answer_callback_query(call.id, "Has marcado la tabla propuesta como erronea.")

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    bot.reply_to(message, "Procesando audio...")
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('user_data/voice_note.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    transcription = whisper_model.transcribe("user_data/voice_note.ogg")
    print("TRANSCRIPTION:\n" + transcription["text"])
    answer = get_table(transcription["text"], message.date, message.from_user.id)
    bot.send_message(message.chat.id, answer, reply_markup=gen_markup(add_buttons=True))

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
    else:
        add_buttons = True
        answer = get_table(message.text, message.date, message.from_user.id)

    bot.send_message(message.chat.id, answer, reply_markup=gen_markup(add_buttons))

bot.infinity_polling()
