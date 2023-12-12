import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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
    
    def get_linealplot(self, message):
        '''
        Gets a message with a var name.
        Returns lineal plot of var_name vs time.
        '''
        data = self.get_data(message.from_user.id)
        var_name = message.text.split()[1]
        lineal_plot = sns.lineplot(x="time", y=var_name, data=data, marker="o")
        lineal_plot.set_xticklabels(lineal_plot.get_xticklabels(), rotation=45, ha='right')
        return(lineal_plot)
    
    def get_countplot(self, message):
        '''
        Gets message.
        Extracts variable name from message text and user_id from
        message's metadata.
        Returns plot.
        '''
        data = self.get_data(message.from_user.id)
        var_name = message.text.split()[1]
        max_num_labels = 5 

        # Set order
        is_numeric = pd.api.types.is_numeric_dtype(data[var_name])
        counts = data[var_name].value_counts()
        if is_numeric:
            my_order = sorted(data[var_name].dropna().unique(), reverse=True)[:max_num_labels]
        else:
            my_order = list(counts[:max_num_labels].index)

        counts = data[var_name].value_counts()

        # Create "other" category
        if len(counts) > max_num_labels:
            other_values = counts[max_num_labels:].index
            data[var_name] = ["Otros" if value in other_values else value for value in data[var_name]]
            my_order += ["Otros"]
        count_plot = sns.countplot(y=var_name, data = data, order=my_order)

        return(count_plot)

    def get_plot(self, message, var_type=None):
        '''
        Gets message with var name.
        Sends plot depending on var type.
        '''
        if len(message.text.split()) == 2:
            var_name = message.text.split()[1]
            answer = "Aquí tienes el gráfico."
            if var_type == None:
                data_structure = self.db.find_one("users", message.from_user.id)["data_structure"]
                var_type = data_structure[var_name]["type"]
                answer = ("Aquí tienes. También puedes especificar el tipo de gráfico"
                          " usando /lineal o /frecuencia seguido del nombre de la variable.")
            if var_type == "Numeric":
                myplot = self.get_linealplot(message)
            else:
                myplot = self.get_countplot(message)
            plt.tight_layout()
            figure = myplot.get_figure()
            filename = f"user_data/{message.from_user.id}_{var_name}.png"
            figure.savefig(filename)
            plt.close()
            with open(filename, "rb") as plot_pic:
                self.bot.send_photo(message.chat.id, photo=plot_pic)
            
        else:
            answer = ("Formato incorrecto. Debes de indicar la variable a mostrar. "
                      "Ej: <code>{command} energy</code>\n"
                      "Para ver la lista de variables disponibles usa "
                      "/variables").format(command=message.text.split()[0])
        return(answer)
    
    def get_variables(self, message):
        '''
        Gets a message.
        Returns user variable names as a string.
        '''
        data_structure = self.db.find_one("users", message.from_user.id)["data_structure"]

        answer = "Estas son las variables disponibles:\n"
        for var_name in data_structure.keys():
            if var_name != "time":
                answer += "- " + var_name + "\n"
        return(answer)


