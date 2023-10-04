from datetime import datetime
import pandas as pd

class Reminders:
    '''
    Manages the unuse score, which represents how important is to add more data
    to each variable.
    '''
    def __init__(self, data_filename, metadata):
        self.data_filename = data_filename
        self.data = pd.read_csv(data_filename, parse_dates=["time"])
        self.metadata = metadata

    def get_score(self, var_name, data):
        '''
        Returns a score representing how unused is the variable.
        The default metric is "number of days withot loggind new data."
        '''
        subdata = data[[var_name, "time"]].dropna()
        try:
            subdata = subdata.sort_values("time")
            last_date = subdata.time.iloc[-1]
            time_diff = datetime.now() - last_date
        except:
            time_diff = pd.Timedelta(days=1000)
        score = time_diff.days
        return(score)


    def get_score_df(self):
        '''
        Returns the last use score for every variable.
        '''
        self.data =  pd.read_csv(self.data_filename, parse_dates=["time"])
        var_names = []
        scores = []
        for var_name in self.metadata.keys():
            if var_name != "time":
                var_names.append(var_name)
                scores.append(self.get_score(var_name, self.data))
        score_df = pd.DataFrame({"var_name":var_names, "score":scores})
        score_df = score_df.sort_values("score", ascending=False, ignore_index=True)
        return(score_df)

    def get_reminders(self):
       ''' Gets dataset(pd.DataFrame)
          Returns advice(str)
       '''
       last_log_df = self.get_score_df()
       last_score = last_log_df.score[0]
       if  last_score > 365:
           last_score = "más de un año"
       else:
           last_score = str(last_score) + " días"
       header = "\n\n" + "_"*25 + "\n\n"
       advice = header + "Hace {time} que no registras {var}, ¿añades una observación?".format(time=last_score,
                                                                                           var=last_log_df.var_name[0])
       return(advice)
