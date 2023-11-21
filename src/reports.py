class Reporter:
    def __init__(self, db, bot):
        self.db = db
        self.bot = bot

    def get_data(self, message):
        '''
        Get data from db.personal and return it as pd.DataFrame
        '''
        user_id = message.from_user.id
        data = None
        return(data)

    def send_data(self, message):
        '''
        get_data(message)
        write data to file
        send file to user
        return some kind of confirmation string
        '''
        data = self.get_data(message)
        answer = "Data sender is still under development."
        return(answer)


