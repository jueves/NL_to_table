import os
import json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
import whisper
from text2table import Text2Table
from reminders import Reminders
from reports import Reporter
from db_utils import MongoManagerPerUser

# Set constants
TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
CHATGPT_KEY = os.environ.get("CHATGPT_KEY")
TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")
WHISPER_TYPE = os.environ.get("WHISPER_TYPE")
WHISPER_LANG= os.environ.get("WHISPER_LANG")
with open("version.txt", "r", encoding="utf8") as f:
    VERSION = f.read()

print("######### VERSION: ", VERSION)

# Load text messages
with open("text/start.txt", "r", encoding="utf-8") as f:
    start_message = f.read()

with open("text/help.txt", "r", encoding="utf-8") as f:
    help_message = f.read()

# Setup Mongo Connection
db = MongoManagerPerUser()

# Setup text to table converter
text2table = Text2Table(db)
reminder = Reminders(db)

# Set default user
with open("config/data_structure.json", "r", encoding="utf-8") as f:
    data_structure = json.load(f)
with open("text/prompt.txt", "r", encoding="utf-8") as f:
    prompt_raw = f.read()
db.insert_one(collection="users", user_id=0, records={"data_structure":data_structure,
                                         "prompt_raw":prompt_raw})

# Setup chatGPT
openai.api_key = CHATGPT_KEY

# Setup Whisper
whisper_model = whisper.load_model(WHISPER_TYPE)

# Setup Telegram bot
bot = telebot.TeleBot(TELEGRAM_KEY)

# Setup reports
reports = Reporter(db, bot)

# Create Telegram message markups
simple_markup = InlineKeyboardMarkup()

# update_markup
update_markup = InlineKeyboardMarkup()
update_markup.row_width = 2
update_markup.add(InlineKeyboardButton("Todo correcto", callback_data="cb_correct"),
                   InlineKeyboardButton("Hay errores", callback_data="cb_errors"))

# load_markup
load_markup = InlineKeyboardMarkup()
load_markup.row_width = 2
load_markup.add(InlineKeyboardButton("Cargar datos", callback_data="cb_load"),
                   InlineKeyboardButton("Cancelar", callback_data="cb_cancel"))


# Set Telegram commands dic
cmd = {"help": ["/help", "/ayuda", "/h"],
       "lastuse": ["/lastuse", "/ultimo_uso"],
       "del": ["/del", "/eliminar", "/borrar"],
       "example": ["/example", "/ejemplo"],
       "getdata": ["/getdata", "/descargar"]
       }

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    '''
    Manages callback for data validation buttons
    '''
    if call.data == "cb_correct":
        text2table.update_dataset(user_id=call.from_user.id)
        bot.answer_callback_query(call.id, "Datos guardados.")
    
    elif call.data == "cb_errors":
        new_csv = text2table.get_correction(call.from_user.id)
        answer = "<code>" + text2table.csv2answer(new_csv, call.from_user.id) + "</code>"
        bot.send_message(call.from_user.id, answer,                                                                                                                                                                                                                                                                                                                 reply_markup=update_markup,
                         parse_mode="html")
    elif call.data == "cb_load":
        text2table.update_dataset(call.from_user.id,
                                  "user_data/dummy_data.csv")
        bot.answer_callback_query(call.id, "Datos de ejemplo cargados.")
    elif call.data == "cb_cancel":
        bot.answer_callback_query(call.id, "No se han cargado los datos.")

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    '''
    Takes a voice note describing data values and answers with a table format propossal.
    '''
    bot.reply_to(message, "Procesando audio...")
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        audio_file = f'user_data/{message.from_user.id}_voice.ogg'
        with open('audio_file', 'wb') as new_file:
            new_file.write(downloaded_file)
        transcription = whisper_model.transcribe("audio_file", language=WHISPER_LANG)
        message.text = transcription["text"]
        print("AUDIO TRANSCRIPTION:\n" + transcription["text"])
        answer = "<code>" + text2table.get_table(message)
        answer += "\nTRANSCRIPCIÓN DE AUDIO:\n" + transcription["text"]
        answer += reminder.get_reminders(user_id=message.from_user.id)  + "</code>"
        markup = update_markup
    except Exception as e:
        answer = f"<b>Algo ha salido mal:</b>\n{e}"
        markup = simple_markup
    bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode="html")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    '''
    Takes all incoming messages and returns answers.
    '''
    markup = simple_markup
    try:
        if not db.user_exists(message.from_user.id):
                db.add_user(message.from_user.id)
        if message.text == "/start":
            answer = start_message + help_message
        elif message.text in cmd["help"]:
            answer = help_message
        elif message.text in cmd["lastuse"]:
            answer = "<code>" + reminder.get_score_df(message.from_user.id).to_markdown(index=False) + "</code>"
        elif message.text.split()[0] in cmd["del"]:
            request_text = text2table.del_request(message)
            answer = "Se ha registrado tu solicitud de borrado. Tu comentario es: " + request_text
        elif message.text in cmd["getdata"]:
            answer = reports.send_data(message)
        elif message.text in cmd["example"]:
            markup = load_markup
            answer = "¿Desea cargar datos ficticios a modo de ejemplo?"
        elif message.text == "/version":
            answer = f"Versión: {VERSION}"
        else:
            markup = update_markup
            answer = "<code>" + text2table.get_table(message) + reminder.get_reminders(message.from_user.id) + "</code>"
    except Exception as e:
        answer = f"<b>Algo ha salido mal:</b>\n{e}"
    bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode="html")

bot.infinity_polling()
