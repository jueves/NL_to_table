import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from icecream import ic

class Reporter:
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot

    def get_data(self, user_id):
        '''
        Get data from db.personal and return it as pd.DataFrame
        '''
        cursor = self.db.find("personal", user_id)
        data = pd.DataFrame(list(cursor))
        data["time"] = pd.to_datetime(data["time"])
        data = data.drop(["_id", "user_id"], axis=1)
        return(data)

    def send_data(self, message):
        '''
        Gets a Telegram Bot message object
        Replies to the chat with user data as a csv file
        Returns text answer as a string.
        '''
        data = self.get_data(message.from_user.id)
        
        csv_file_name = f"user_data/{str(message.from_user.id)}_full.csv"
        data.to_csv(csv_file_name)
        with open(csv_file_name, "r") as csv_file:
            self.bot.send_document(message.chat.id, reply_to_message_id=message.message_id,
                                    document=csv_file)
        answer = "Aquí tiene sus datos."
        return(answer)
    
    def get_lineal(self, message):
        '''
        Plots var_name vs time and sends it as a picture.
        '''
        data = self.get_data(message.from_user.id)
        var_name = message.text.split()[1]
        #plt.xticks(rotation=45, ha='right')
        lineal_plot = sns.lineplot(x="time", y=var_name, data=data)
        lineal_plot.set_xticklabels(lineal_plot.get_xticklabels(), rotation=45, ha='right')
        plt.tight_layout()
        figure = lineal_plot.get_figure()
        filename = f"user_data/{message.from_user.id}_{var_name}.png"
        figure.savefig(filename)
        plt.close()
        with open(filename, "rb") as plot_pic:
            self.bot.send_photo(message.chat.id, photo=plot_pic)


