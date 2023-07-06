import telebot
import json
import datetime
import openai

# Load keys
with open(".keys.json", "r") as f:
    keys_dic = json.load(f)

# Setup chatGPT
openai.my_api_key = keys_dic["chatGPT"]
messages = [ {"role": "system", "content": "You are a intelligent assistant."} ]

def text_to_table(text):
	messages.append({"role": "user", "content": text},)
	
    chat = openai.ChatCompletion.create(
	        model="gpt-3.5-turbo", messages=messages
		)
	
	reply = chat.choices[0].message.content
	return(reply)





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
