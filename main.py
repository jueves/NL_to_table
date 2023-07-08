import telebot
import json
from datetime import datetime
import pandas as pd
from io import StringIO
import openai
from sanity_check import sanity_check

# Load keys
with open("keys.json", "r") as f:
    keys_dic = json.load(f)

# Load prompt header
with open("prompt_header.txt", "r") as f:
    prompt_header = f.read()


# Setup chatGPT
openai.api_key = keys_dic["chatGPT"]
messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]

# chatGPT functions
def just_chat(text):
    messages.append({"role": "user", "content": text})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    
    reply = chat.choices[0].message.content
    return(reply)

def message_to_csv(message):
    message_time = datetime.utcfromtimestamp(message.date)
    timestr = message_time.strftime("%d.%m.%Y %H:%M:%S  ")
    txt_input = prompt_header + timestr + message.text

    messages.append({"role": "user", "content": txt_input})
    chat = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    
    reply = chat.choices[0].message.content
    return(reply)


# Telegram bot
bot = telebot.TeleBot(keys_dic["telegram"])

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    if (message.text[:4] == "chat"):
        answer = just_chat(message.text[5:])
    elif (message.text == "hora"):
        answer = str(datetime.now())
    else:       
        csv_data = message_to_csv(message)
        data = pd.read_csv(StringIO(csv_data))
        answer = sanity_check(data)

    bot.reply_to(message, answer)

bot.infinity_polling()
