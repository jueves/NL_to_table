FROM python

RUN pip install pyTelegramBotAPI pandas openai tabulate openai-whisper

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /NL_to_table

COPY data_structure.json start.txt help.txt prompt_header.txt main.py sanity_check.py /NL_to_table/

CMD python main.py
