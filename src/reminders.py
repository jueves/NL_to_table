from datetime import datetime
import pandas as pd

class Reminders:
    '''
    Manages the unuse score, which represents how important is to add more data
    to each variable.
    '''
    def __init__(self, db):
        self.db = db

    def get_score(self, user_id, var_name):
        '''
        Returns a score representing how unused is the variable.
        The default metric is "number of days without logging new data."
        '''
        try:
            lastuse_dict = self.db.find_one(collection="lastuse", user_id=user_id,
                                             sort=[('time', -1)], projection={"_id":0})
            time_diff = datetime.now() - lastuse_dict[var_name]
        except:
            time_diff = pd.Timedelta(days=1000)
        score = time_diff.days
        return(score)


    def get_score_df(self, user_id):
        '''
        Returns the last use score for every variable.
        '''
        var_names = []
        scores = []
        data_structure = self.db.find_one("users", user_id)["data_structure"]
        for var_name, var_metadata in data_structure.items():
            if var_name != "time" and var_metadata["mute"] == "False":
                var_names.append(var_name)
                scores.append(self.get_score(user_id, var_name))
        score_df = pd.DataFrame({"var_name":var_names, "days_unused":scores})
        score_df = score_df.sort_values("days_unused", ascending=False, ignore_index=True)
        return(score_df)

    def get_reminders(self, user_id):
       ''' Gets dataset as pd.DataFrame
          Returns advice as str
       '''
       lastuse_df = self.get_score_df(user_id)
       
       last_score = lastuse_df.days_unused[0]
       last_var_name = lastuse_df.var_name[0]
       
       if  last_score > 365:
           last_score = "más de un año"
       else:
           last_score = str(last_score) + " días"
       header = "\n\n" + "_"*25 + "\n\n"
       advice = header + "Hace {time} que no registras {var}, ¿añades una observación?".format(time=last_score,
                                                                                           var=last_var_name)

       return(advice)
