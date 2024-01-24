# NL_to_table
_**TL;DR:** Bot that converts natural language to table. [Try me!](https://t.me/cuadriculado_bot)_

This is a Telegram Bot that converts text and voice to tables using Whisper and ChatGPT. The table format is specified in `data_structure.json`. This file serves both to build the prompts and to assist on data operations.

All info messages are in Spanish, but your data and variables can be in any language. ChatGPT will convert the variable names to whatever language is describing data in `data_structure.json`.

<a href="https://t.me/cuadriculado_bot">
  <img src="https://user.fm/files/v2-289cafe11637f40dc480d218d7814927/NL_to_table_screenshot_L.png" alt="Screenshot">
</a>

# Installation
1. Install Docker on your machine.
2. Set your own `.env` file from `.env_example`.
      - `TELEGRAM_KEY` Your Telegram Bot Key. You can get it texting to [@BotFather](https://t.me/BotFather) on Telegram.
      - `OPENAI_API_KEY` Your OpenAI API key to use with ChatGPT. You can get it [here](https://platform.openai.com/account/api-keys).
      - `WHISPER_MODEL` The language model to use. Be aware that if the model is too large for your hardware, the app will crash. You can choose between _tiny_, _base_, _small_, _medium_, _large_, _large-v2_ and _large-v3_.
      - `WHISPER_LANG` Whisper will assume all audio comes in this language.
      - `MONGO_USER` The username to use in your Mongo Database.
      - `MONGO_PASSWORD` Your Mongo password.

3. Run the bot using Docker Compose. You can either clone the project and build the image with [docker-compose.yml](https://github.com/jueves/NL_to_table/blob/main/docker-compose.yml) or use a prebuild image from DockerHub running Docker Compose with [production.yml](https://github.com/jueves/NL_to_table/blob/main/docker/production.yml).

# Configuration
You can get your own `data_structure.json` config file with the `/getconf` command. You will be sent instructions explaining the diferent fields to set. You can create and delete any variable you want as long as you define it with the proper structure. Once done, you can send it back to the bot and it will be set for your future data logs. This does not affect your old data.

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
You can load dummy data in order to test the app using the `/example` command. To remove dummy data, use the `/deldummy`command.`

## Plots
You have two diferent plots you can use for quick basic exploration:
- `/count` for a single variable counting barplot.
- `/lineal` for variable vs time lineplot.
- You can also use just use `/plot` and it will be chosen for you.
