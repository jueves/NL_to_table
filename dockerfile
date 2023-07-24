FROM python

RUN pip install pyTelegramBotAPI pandas openai tabulate openai-whisper

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /NL_to_table

COPY data_structure.json start.txt help.txt prompt_A1.txt prompt_B1.txt main.py sanity_check.py /NL_to_table/

COPY user_data/data_example.csv /NL_to_table/user_data/data.csv

CMD python main.py
