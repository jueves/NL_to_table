import os
import json
from table_processing import Text2Table, Reminders


# Load variables in .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    print("Error loading dotenv, .env file won't be used.")

# Set constants
DATA_FILENAME = "user_data/data.csv"
PROMPT_FILENAME = "text/prompt.txt"
TELEGRAM_KEY = os.environ.get("TELEGRAM_KEY")
CHATGPT_KEY = os.environ.get("CHATGPT_KEY")
TELEGRAM_USER_ID = os.environ.get("TELEGRAM_USER_ID")
WHISPER_TYPE = os.environ.get("WHISPER_TYPE")
WHISPER_LANG= os.environ.get("WHISPER_LANG")

# Load text messages
with open("data_structure.json", "r", encoding="utf-8") as f:
    DATA_STRUCTURE = json.load(f)

# Setup text to table converter
text2table = Text2Table(DATA_STRUCTURE, PROMPT_FILENAME, TELEGRAM_USER_ID, DATA_FILENAME)
reminder = Reminders(DATA_FILENAME, DATA_STRUCTURE)
