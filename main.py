import telebot
import json
import datetime

with open(".keys.json", "r") as f:
    keys_dic = json.load(f)

def text_to_table(text):
    



bot = telebot.TeleBot(keys_dic["telegram"])

@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    if (message.text == "Hola"):
        answer = "¡Hola!"
    elif (message.text == "hora"):
        answer = str(datetime.datetime.now())
    bot.reply_to(message, answer)

#Launches the bot in infinite loop mode with additional
#...exception handling, which allows the bot
#...to work even in case of errors. 
bot.infinity_polling()
