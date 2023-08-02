import os
import json
import telebot
import openai
import whisper
from table_processing import Text2Table

# Set constants
DATA_FILENAME = "user_data/data.csv"
PROMPT_FILENAME = "text/prompt.txt"
TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
CHATGPT_KEY = os.environ.get("CHATGPT_KEY")
TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")

# Load text messages
with open("data_structure.json", "r", encoding="utf-8") as f:
    DATA_STRUCTURE = json.load(f)

with open("text/start.txt", "r", encoding="utf-8") as f:
    start_message = f.read()

with open("text/help.txt", "r", encoding="utf-8") as f:
    help_message = f.read()

# Setup text to table converter
text2table = Text2Table(DATA_STRUCTURE, PROMPT_FILENAME, TELEGRAM_USER_ID, DATA_FILENAME)

# Setup chatGPT
openai.api_key = CHATGPT_KEY

# Setup Whisper
whisper_model = whisper.load_model("base")

# Setup Telegram bot
bot = telebot.TeleBot(TELEGRAM_KEY)

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
        bot.answer_callback_query(call.id, "Has marcado la tabla propuesta como erronea.")

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
    transcription = whisper_model.transcribe("user_data/voice_note.ogg")
    print("TRANSCRIPTION:\n" + transcription["text"])
    answer = text2table.get_table(transcription["text"], message.date, message.from_user.id)
    bot.send_message(message.chat.id, answer, reply_markup=text2table.gen_markup(add_buttons=True))

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
        answer = json.dumps(DATA_STRUCTURE, indent=4)
    else:
        add_buttons = True
        answer = text2table.get_table(message.text, message.date, message.from_user.id)

    bot.send_message(message.chat.id, answer, reply_markup=text2table.gen_markup(add_buttons))

bot.infinity_polling()
