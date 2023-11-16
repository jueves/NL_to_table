from datetime import datetime
import pandas as pd

class Reminders:
    '''
    Manages the unuse score, which represents how important is to add more data
    to each variable.
    '''
    def __init__(self, mongodb, metadata):
        self.mongo_lastuse = mongodb["lastuse"]
        self.metadata = metadata

    def get_score(self, var_name):
        '''
        Returns a score representing how unused is the variable.
        The default metric is "number of days without logging new data."
        '''
        try:
            lastuse_dict = self.mongo_lastuse.find_one(sort=[('time', -1)],
                                                       projection={"_id":0})
            time_diff = datetime.now() - lastuse_dict[var_name]
        except:
            time_diff = pd.Timedelta(days=1000)
        score = time_diff.days
        return(score)


    def get_score_df(self):
        '''
        Returns the last use score for every variable.
        '''
        var_names = []
        scores = []
        for var_name, var_metadata in self.metadata.items():
            if var_name != "time" and var_metadata["mute"] == "False":
                var_names.append(var_name)
                scores.append(self.get_score(var_name))
        score_df = pd.DataFrame({"var_name":var_names, "score":scores})
        score_df = score_df.sort_values("score", ascending=False, ignore_index=True)
        return(score_df)

    def get_reminders(self):
       ''' Gets dataset(pd.DataFrame)
          Returns advice(str)
       '''
       lastuse_df = self.get_score_df()
       
       last_score = lastuse_df.score[0]
       last_var_name = lastuse_df.var_name[0]
       
       if  last_score > 365:
           last_score = "más de un año"
       else:
           last_score = str(last_score) + " días"
       header = "\n\n" + "_"*25 + "\n\n"
       advice = header + "Hace {time} que no registras {var}, ¿añades una observación?".format(time=last_score,
                                                                                           var=last_var_name)

       return(advice)
