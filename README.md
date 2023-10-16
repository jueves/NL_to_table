# NL_to_table
Natural language to table converter.

This is a Telegram Bot that converts text and voice to tables using Whisper and ChatGPT. The table format is specified in `data_structure.json`. This file serves both to build the prompts and the help message.

All info messages are in Spanish, but your data and variables can be in any language. ChatGPT will convert the messages to whatever language is describing data in `data_structure.json`.

Every user gets it's own response, but only the user whose id is in the settings will get its data logged.

# Installation
1. Install Docker on your machine.
2. Set your own `.env` file from `.env_example`.
      - `TELEGRAM_KEY` Your Telegram Bot Key. You can get it texting to @BotFather on Telegram.
      - `CHATGPT_KEY` Your ChatGPT API key. You can get it on openai.com
      - `TELEGRAM_USER_ID` Your own user id. You can get it texting to @userinfobot on Telegram.
      - `WHISPER_TYPE` The language model to use. If the model is too large for your hardware the app will crash.
      - `WHISPER_LANG` Whisper will assume all audio comes in this language. 

3. Download `user_data/data_example.csv` and rename it as `user_data/data.csv`
4. Run the bot using Docker compose.

# Configuration
- You can easily adapt the bot to your needs by downloading and editing `data_structure.json` and then mounting it on `/NL_to_table/`  
- You can also change Whisper model type and default language under the environment section in the compose file.

# Usage
## Log new data
1. Send a message to your bot, either a voice note or a text, with one or more variable values.
2. You will be answered with your input in table format. If your input was a voice note, you will also get the Whisper transcription. At the foot of the message you will get two buttons, one to aprove it and one to get a correction.
3. If you aprove the message and you are the owner (your user id is the one in the settings) your data will be saved. If you ask for a correction nothing will be saved and you will get a new propossal.

## Delete last log
To create a deletion requests, use the `/del` command followed by a comment. For example: `/del That last alergy measure of 3 wasn't real, it was a test.`  
This will get logged in `user_data/deletion_requests.json` to be reviewed by the admin.  

## Reminders
Anytime you add new data you will be reminded of the variable that has been unrecorded for the longest time.  
Variables muted in `data_structure.json` are excluded from reminders.

# To do
- [X] Include reminders for varibles not used in a long time.
- [ ] Use a database.
- [ ] Return descriptive data visualizations.
