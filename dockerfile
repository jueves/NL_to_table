FROM python:alpine

RUN pip install pyTelegramBotAPI pandas openai

WORKDIR /NL_to_table

COPY . /NL_to_table

CMD python main.py