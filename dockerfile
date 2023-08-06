FROM python

RUN pip install openai-whisper pyTelegramBotAPI openai

RUN apt-get update && apt-get install -y ffmpeg

RUN pip install pandas tabulate 

WORKDIR /NL_to_table

COPY data_structure.json main.py sanity_check.py table_processing.py /NL_to_table/

COPY text/* /NL_to_table/text/

COPY user_data/data_example.csv /NL_to_table/user_data/data.csv

CMD python main.py
