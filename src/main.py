import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai
from audio_utils import Whisper4Bot
from text2table import Text2Table
from reminders import Reminders
from reports import Reporter
from db_utils import MongoManagerPerUser
from user_manager import UserManager

# Set constants
TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")

with open("version.txt", "r", encoding="utf8") as f:
    VERSION = f.read()
print("######### VERSION: ", VERSION)

# Load text messages
with open("text/start.txt", "r", encoding="utf-8") as f:
    start_message = f.read()

with open("text/help.txt", "r", encoding="utf-8") as f:
    help_message = f.read()

with open("text/config_instructions.txt", "r", encoding="utf-8") as f:
    config_instructions = f.read()


# Setup Mongo Connection
db = MongoManagerPerUser()

# Setup text to table converter
text2table = Text2Table(db)
reminder = Reminders(db)

# Setup chatGPT
openai.api_key = OPENAI_API_KEY

# Setup Telegram bot
bot = telebot.TeleBot(TELEGRAM_KEY)

# Setup reports
reports = Reporter(db, bot)

# Setup user_manager
user_manager = UserManager(db, bot)

# Setup audio2text
audio2text = Whisper4Bot(bot)

# Create Telegram message markups
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

# del_markup
del_markup = InlineKeyboardMarkup()
del_markup.row_width = 2
del_markup.add(InlineKeyboardButton("Borrar registro", callback_data="cb_del"),
               InlineKeyboardButton("Mostrar otro", callback_data="cb_keep"),
               InlineKeyboardButton("Cancelar", callback_data="cb_cancel"))

# Set Telegram commands dic
cmd = {"help": ["/help", "/ayuda", "/h"],
       "lastuse": ["/lastuse", "/ultimo_uso"],
       "del": ["/del", "/eliminar", "/borrar"],
       "admin_del": ["/admin_del", "/borrado_admin"],
       "example": ["/example", "/ejemplo"],
       "getdata": ["/getdata", "/descargar"],
       "getconf": ["/getconf", "/configurar"],
       "lineal": ["/lineal"],
       "count": ["/count", "/frecuencia", "/frec"],
       "plot": ["/plot", "/grafico"],
       "vars": ["/variables", "/vars"]
       }

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    '''
    Manages callback for confirmation buttons
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
        bot.answer_callback_query(call.id, "Operación cancelada.")
        
    elif call.data == "cb_del":
        db.delete_using_call(call)
        bot.answer_callback_query(call.id, "Respuesta a la solicitud de borrado.")

    elif call.data == "cb_keep":
        answer = ("Para elegir el último registro, usa <code>/eliminar</code>,"
                  " para el penúltimo usa <code>/eliminar 1</code>, para el anterior"
                  " a este <code>/eliminar 2</code> y así sucesivamente.\n"
                  "También puedes dejar una solicitud de eliminación usando /borrado_admin"
                  " seguido de un comentario descriptivo.")
        bot.send_message(call.from_user.id, answer, parse_mode="html")

    # Remove the buttons to prevent new actions
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.message_handler(content_types=['voice'])
def voice_processing(message):
    '''
    Takes a voice note describing data values and answers with a table format propossal.
    '''
    try:
        is_available, transcription_text =  audio2text.transcribe(message)
        if is_available:
            message.text = transcription_text
            answer = "<code>" + text2table.get_table(message)
            answer += "\nTRANSCRIPCIÓN DE AUDIO:\n" + transcription_text
            answer += reminder.get_reminders(user_id=message.from_user.id)  + "</code>"
            markup = update_markup
        else:
            answer = "El modelo Whisper está ocupado, inténtelo de nuevo en unos minutos."
            markup = None
    except Exception as e:
        answer = f"<b>Algo ha salido mal:</b>\n{e}"
        markup = None
    bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode="html")

@bot.message_handler(content_types=['document'])
def document_processing(message):
    '''
    Gets a message with a file.
    Validates file structure matchs configuration file.
    Sets configuration for the user.
    '''
    if message.document.file_name[-19:] == "data_structure.json":
        try:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            filename = f'user_data/{message.from_user.id}_data_structure.json'
            with open(filename, 'wb') as new_file:
                new_file.write(downloaded_file)
            answer = user_manager.set_data_structure(message.from_user.id, filename)
        except Exception as e:
            answer = f"<b>Algo ha salido mal:</b>\n{e}"
    else:
        answer = ("Solo acepto archivos de configuración. Estos han de llevar un"
                  "nombre acabado en 'data_structure.json'")
    bot.send_message(message.chat.id, answer, parse_mode="html")

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    '''
    Takes all incoming messages and returns answers.
    '''
    markup = None
    try:
        if not user_manager.user_exists(message.from_user.id):
                user_manager.add_user(message.from_user.id)
        if message.text == "/start":
            answer = start_message + help_message
        elif message.text in cmd["help"]:
            answer = help_message
        elif message.text in cmd["lastuse"]:
            answer = "<code>" + reminder.get_score_df(message.from_user.id).to_markdown(index=False) + "</code>"
        elif message.text.split()[0] in cmd["del"]:
            markup = del_markup
            answer = text2table.get_deletion_proposal(message)
        elif message.text.split()[0] in cmd["admin_del"]:
            answer = db.admin_del_request(message)
        elif message.text in cmd["getdata"]:
            answer = reports.send_data(message)
        elif message.text in cmd["example"]:
            markup = load_markup
            answer = "¿Desea cargar datos ficticios a modo de ejemplo?"
        elif message.text in cmd["getconf"]:
            user_manager.send_data_structure(message)
            answer = config_instructions
        elif message.text.split()[0] in cmd["lineal"]:
            answer = reports.get_plot(message, var_type="Numeric")
        elif message.text.split()[0] in cmd["count"]:
            answer = reports.get_plot(message, var_type="any")
        elif message.text.split()[0] in cmd["plot"]:
            answer = reports.get_plot(message)
        elif message.text in cmd["vars"]:
            answer = reports.get_variables(message)
        elif message.text == "/version":
            answer = f"Versión: {VERSION}"
        else:
            markup = update_markup
            answer = ("<code>" + text2table.get_table(message) + "</code>" +
                      reminder.get_reminders(message.from_user.id))
    except Exception as e:
        answer = f"<b>Algo ha salido mal:</b>\n{e}"
    bot.send_message(message.chat.id, answer, reply_markup=markup, parse_mode="html")

bot.infinity_polling()
    