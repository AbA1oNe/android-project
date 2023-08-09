import pandas as pd
import json

def transform(): #load json into dataframe
    with open('data.json', 'r') as jsonFile:
        data = json.load(jsonFile)
        numSubject = len(data)
        dfList = []
        df = pd.DataFrame()
        df1 = pd.DataFrame()

        
        for col in data[next(iter(data))][0]: #initialize the columns of the dataframe
            if (col != "timestamp"):
                df[col] = ""
                df1[col] = ""
        
        for i in range(numSubject):           
            for username in data:
                for dict in data[username]:
                    for key, value in dict.items():
                        if (key != "timestamp"):
                            
                            if (list(data)[i] == username and key == "label"):
                                df1[key] = 1
                            else:
                                df1[key] = [value]
                            
                            if (key == "sizeMedian" and df1["pressureMedian"][0] == 1):
                                df1["pressureMedian"] = [value]
                    df = pd.concat([df,df1])
            dfList.append(df)
            
            df = pd.DataFrame()
            df1 = pd.DataFrame()
            for col in data[next(iter(data))][0]: #initialize the columns of the dataframe
                if (col != "timestamp"):
                    df[col] = ""
                    df1[col] = ""
                
    return dfList

pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
#data = transform()
#print(data.head(5))
#dfList = transform()
#print(len(dfList))
#print(dfList[0].head(5))
#print("-------------------")
#print(dfList[1].head())