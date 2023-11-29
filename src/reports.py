import pandas as pd

class Reporter:
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot

    def get_data(self, message):
        '''
        Get data from db.personal and return it as pd.DataFrame
        '''
        cursor = self.db.find("personal", message.from_user.id)
        data = pd.DataFrame(list(cursor))
        data = data.drop(["_id", "user_id"], axis=1)
        return(data)

    def send_data(self, message):
        '''
        Gets a Telegram Bot message object
        Replies to the chat with user data as a csv file
        Returns text answer as a string.
        '''
        data = self.get_data(message)
        
        csv_file_name = f"user_data/{str(message.from_user.id)}_full.csv"
        data.to_csv(csv_file_name)
        with open(csv_file_name, "r") as csv_file:
            self.bot.send_document(message.chat.id, reply_to_message_id=message.message_id,
                                    document=csv_file)
        answer = "Aquí tiene sus datos."
        return(answer)


