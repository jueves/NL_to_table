# NL_to_table
Natural language to table converter.

This is a Telegram Bot that converts text and voice to tables using Whisper and ChatGPT. The table format is specified in `data_structure.json`. This file serves both to build the prompts and the help message.

All info messages are in Spanish, but your data and variables can be in any language.

Every user gets it's own response, but only the user whose id is in the settings will get its data logged.

# Installation
1. Install [Docker](https://www.docker.com) in your machine.
2. Download `NL_to_table.yml` and fill it with your own keys and settings.
3. Download `user_data/data_example.csv` and rename it as `user_data/data.csv`
4. Run on Docker using the `NL_to_table.yml` compose file.

# Configuration
- You can easily adapt the bot to your needs by downloading and editing `data_structure.json` and then mounting it on `/NL_to_table/`  
- You can also change Whisper model type and default language under the environment section in the compose file.

# Ussage
1. Send a message to your bot, either a voice note or a text, with one or more variable values.
2. You will be answered with your input in table format. If your input was a voice note, you will also get the Whisper transcription. At the foot of the message you will get two buttons, one to aprove it and one to get a correction.
3. If you aprove the message and you are the owner (your user id is the one in the settings) your data will be saved. If you ask for a correction nothing will be saved and you will get a new propossal.



# To do
- [x] Include more variables.
- [X] Improve Readme.
- [x] Include reminders for varibles not used in a long time.
- [ ] Check if results could be improved by keeping longer conversations. Only reset chat on user command.
