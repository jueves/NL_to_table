FROM python

RUN pip install pyTelegramBotAPI pandas openai tabulate

WORKDIR /NL_to_table

COPY . /NL_to_table

CMD python main.py
