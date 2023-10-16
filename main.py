import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
import whisper
from text2table import Text2Table
from reminders import Reminders

# Load variables in .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("Error loading dotenv, .env file won't be used.")

# Set constants
DATA_FILENAME = "user_data/data.csv"
TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
CHATGPT_KEY = os.environ.get("CHATGPT_KEY")
TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")
WHISPER_TYPE = os.environ.get("WHISPER_TYPE")
WHISPER_LANG= os.environ.get("WHISPER_LANG")

print("##### VARIABLE IMPORTADA:\n", TELEGRAM_KEY)

# Load text messages
with open("data_structure.json", "r", encoding="utf-8") as f:
    DATA_STRUCTURE = json.load(f)

with open("text/start.txt", "r", encoding="utf-8") as f:
    start_message = f.read()

with open("text/help.txt", "r", encoding="utf-8") as f:
    help_message = f.read()

with open("text/prompt.txt", "r", encoding="utf-8") as f:
    prompt_raw = f.read()


# Setup text to table converter
text2table = Text2Table(DATA_STRUCTURE, prompt_raw, TELEGRAM_USER_ID, DATA_FILENAME)
reminder = Reminders(DATA_FILENAME, DATA_STRUCTURE)

# Setup chatGPT
openai.api_key = CHATGPT_KEY

# Setup Whisper
whisper_model = whisper.load_model(WHISPER_TYPE)

# Setup Telegram bot
bot = telebot.TeleBot(TELEGRAM_KEY)

# Create Telegram message markups
simple_markup = InlineKeyboardMarkup()
buttons_markup = InlineKeyboardMarkup()
buttons_markup.row_width = 2
buttons_markup.add(InlineKeyboardButton("Todo correcto", callback_data="cb_correct"),
                   InlineKeyboardButton("Hay errores", callback_data="cb_errors"))



@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    '''
    Manages callback for data validation buttons
    '''
    if call.data == "cb_correct":
        if (str(call.from_user.id) == TELEGRAM_USER_ID):
            # Only saves data for user_id
            text2table.update_dataset()
            bot.answer_callback_query(call.id, "Datos guardados.")

        else:
            bot.answer_callback_query(call.id, "Has confirmado la tabla propuesta.")
    
    elif call.data == "cb_errors":
        new_csv = text2table.get_correction(call.from_user.id)
        answer = "<code>" + text2table.csv2answer(new_csv, call.from_user.id) + "</code>"
        bot.send_message(call.from_user.id, answer,                                                                                                                                                                                                                                                                                                                 reply_markup=buttons_markup,
                         parse_mode="html")

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    '''
    Takes a voice note describing data values and answers with a table format propossal.
    '''
    bot.reply_to(message, "Procesando audio...")
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open('user_data/voice_note.ogg', 'wb') as new_file:
        new_file.write(downloaded_file)
    transcription = whisper_model.transcribe("user_data/voice_note.ogg", language=WHISPER_LANG)
    message.text = transcription["text"]
    answer = "<code>" + text2table.get_table(message)
    print("AUDIO TRANSCRIPTION:\n" + transcription["text"])
    answer += "\nTRANSCRIPCIÓN DE AUDIO:\n" + transcription["text"]
    answer += reminder.get_reminders()  + "</code>"
    bot.send_message(message.chat.id, answer, reply_markup=buttons_markup, parse_mode="html")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    '''
    Takes all incoming messages and returns answers.
    '''
    markup = simple_markup
    if message.text == "/start":
        answer = start_message + help_message
    elif message.text == "/help":
        answer = help_message
    elif message.text == "/metadata":
        answer = "<code>" + json.dumps(DATA_STRUCTURE, indent=4) + "</code>"
    elif message.text == "/lastlog":
        answer = "<code>" + reminder.get_score_df().to_markdown(index=False) + "</code>"
    elif message.text[:4] == "/del":
        text2table.del_request(message)
        answer = "Se ha registrado tu solicitud de borrado. Tu comentario es: " + message.text[4:]
    else:
        markup = buttons_markup
        answer = "<code>" + text2table.get_table(message) + reminder.get_reminders() + "</code>"

    bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode="html")

bot.infinity_polling()
