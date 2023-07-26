import pandas as pd
import json

class Train():    
    def transform(): #load json into dataframe
        with open('data.json', 'r') as jsonFile:
            data = json.load(jsonFile)
            df = pd.DataFrame()
            
            for col in data[next(iter(data))][0]: #initialize the columns of the dataframe
                if (col != "timestamp"):
                    df[col] = ""
            
            for username in data:
                for dict in data[username]:
                    i = 0
                    for key, value in dict.items():
                        if (key != "timestamp"):
                            df[key] = [value]
                            
        return df

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
#data = Train.transform()