FROM python:3.11.2

RUN pip install openai==0.28.0 openai-whisper==20230918 pyTelegramBotAPI==4.13.0

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install pandas==2.1.0 tabulate==0.9.0 pymongo==4.5.0

WORKDIR /NL_to_table

COPY data_structure.json main.py sanity_check.py text2table.py reminders.py db_utils.py load_old_data_to_mongo.py /NL_to_table/

COPY text/* /NL_to_table/text/

COPY user_data/data_example.csv /NL_to_table/user_data/data.csv

CMD python main.py
