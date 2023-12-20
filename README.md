# NL_to_table
_**TL;DR:** Bot that converts natural language to table. [Try me!](https://t.me/cuadriculado_bot)_

This is a Telegram Bot that converts text and voice to tables using Whisper and ChatGPT. The table format is specified in `data_structure.json`. This file serves both to build the prompts and to assist on data operations.

All info messages are in Spanish, but your data and variables can be in any language. ChatGPT will convert the variable names to whatever language is describing data in `data_structure.json`.

# Installation
1. Install Docker on your machine.
2. Set your own `.env` file from `.env_example`.
      - `TELEGRAM_KEY` Your Telegram Bot Key. You can get it texting to [@BotFather](https://t.me/BotFather) on Telegram.
      - `CHATGPT_KEY` Your ChatGPT API key. You can get it [here](https://platform.openai.com/account/api-keys).
      - `WHISPER_TYPE` The language model to use. Be aware that if the model is too large for your hardware the app will crash.
      - `WHISPER_LANG` Whisper will assume all audio comes in this language. 

3. Run the bot using Docker Compose.

# Configuration
You can get your config file with the `/getconf` command. You will be sent instructions explaining the diferent fields to set. You can create and delete any variable you want as long as you define it with the proper structure. Once done, you can send it back to the bot and it will be set for your future data logs. This does not affect your old data.

# Usage
## Log new data
1. Send a message to your bot, either a voice note or a text, with one or more variable values.
2. You will be answered with your input in table format. If your input was a voice note, you will also get the Whisper transcription. At the foot of the message you will get two buttons, one to aprove it and one to get a correction.
3. If you aprove the message your data will be saved. If you ask for a correction nothing will be saved and you will get a new propossal.

## Delete last log
To delete the last record, use the `/del` command. If you want to delete the record before that, you have to use `/del 1`, for the previous one `/del 2`, etc... You will be shown the data to remove and asked for confirmation.
If you have problems with this you can always send a deletetion request to the admin using `/admin_del` followed by a comment describing the problem.

## Check available variables
You can use the command `/vars` to get a list of all available variables.

## Reminders
Anytime you add new data you will be reminded of the variable that has been unrecorded for the longest time.  
Variables muted in `data_structure.json` are excluded from reminders.

## Download dataset
You can download all your data in a csv file using the command `/download`

## Dummy data
You can load dummy data in order to test the app using the `/example` command.

## Plots
You have two diferent plots you can use for quick basic exploration:
- `/count` for a single variable counting barplot.
- `/lineal` for variable vs time lineplot.
- You can also use just use `/plot` and it will be chosen for you.
