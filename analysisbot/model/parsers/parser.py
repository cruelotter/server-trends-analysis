import os
import pickle
from datetime import date, datetime, time

from analysisbot.database.mongodb import MongoManager
from analysisbot.model.analysis.preprocessing import Preprocessing

class Parser(object):
    type = "undefined"
    preprocessor = Preprocessing()
    
    def __init__(self) -> None:
        self.preprocessor = Preprocessing()
 
    def save_and_clear(self, raw_data, source: str, date: date):
        path = "./storage/data/{}/{}/{}/{}".format(self.type, source, date.year, str(date.month).zfill(2))
        os.makedirs(path[:-3], exist_ok=True)
        print(path)
        with open(file=path+"raw.pkl", mode="wb") as file:
            pickle.dump(raw_data, file)
            
        stats_data = self.preprocessor.raw_to_stats(raw_data, path)
        stats_data.to_csv(path+"stats.csv")
        del stats_data
        raw_data.clear()
        raw_data = []
        
        # if raw_data!=[]:
        MongoManager.update_data(
            'processed_data',
            {"type": self.type, "source": source, "year": date.year, "month": date.month}, 
            {"full": datetime.combine(datetime.now().date, time(23,59))}
        )
        # else:
        #     MongoManager.update_data(
        #         'processed_data',
        #         {"type": self.type, "source": source, "year": date.year, "month": date.month}, 
        #         {"full": datetime(1900, 1,1)}
        #     )
    
    def get_source_data(self, chat_name: str, queue):
        pass
    