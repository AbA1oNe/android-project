import pandas as pd
import json

def transform(file): #load json into dataframe
    with open(file, 'r') as jsonFile:
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

def onlyOneUser(file, username):
    with open(file, 'r') as jsonFile:
        data = json.load(jsonFile)
        df = pd.DataFrame()
        df1 = pd.DataFrame()
        
        for col in data[next(iter(data))][0]: #initialize the columns of the dataframe
            if (col != "timestamp"):
                df[col] = ""
                df1[col] = ""

        print(len(data[username]))
        for dict in data[username]:
            for key, value in dict.items():
                if (key != "timestamp" and key != "label"):
                    df1[key] = [value]
                elif key == "label":
                    df1[key] = 1
            df = pd.concat([df,df1])

    return df
    
def addNewData():
    userList = ["1092954", "dama0623", "1094908", "4109034029", "611034", "1094841", "D1186959",
                "411411159", "1094845", "1094842", "110", "pomiii5093", "1092574", "anyu5471", "px",
                "wardlin", "lenny", "1092960", "1092923", "1092950", "1092942", "1092928", "1092922"]
    
    dfList = transform("data.json")
    with open("temp.json", 'r') as jsonFile:
        data = json.load(jsonFile)
        for user in data:
            index = userList.index(user)
            df = pd.DataFrame()
            df = onlyOneUser("temp.json", user).sample(frac=0.5)
            
            dfList[index] = pd.concat([dfList[index], df])
    
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