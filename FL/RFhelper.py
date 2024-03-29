import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import json
import numpy as np
import train
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from typing import List

def load_dataset(client_id: int):
    userOrder = []
    userList = ["1092954", "dama0623", "1094908", "4109034029", "611034", "1094841", "D1186959",
                "411411159", "1094845", "1094842", "110", "pomiii5093", "1092574", "anyu5471", "px",
                "lenny", "1092960", "1092923", "1092950", "1092942", "1092928", "1092922", "29282928"]

    #'''
    with open("../evaluationData.json", 'r') as f:
        data = json.load(f)
        for i in data.keys():
            userOrder.append(userList.index(i))
    #'''

    dfList = train.transform("../data.json") #15 is wardlin , which is not collected in temp.json
    #'''
    with open("../temp.json", 'r') as jsonFile:
        data = json.load(jsonFile)
        for user in data:
            index = userList.index(user)
            df = pd.DataFrame()
            df = train.onlyOneUser("C:\\Main\\Code\\ml-app\\temp.json", user)

            length = len(df)

            df = shuffle(df, random_state=42)
            df = df[:length//2] #first half for training, second half for testing

            dfList[index] = pd.concat([dfList[index], df])
    #'''

    dfListTest = train.transformSplit("C:\\Main\\Code\\ml-app\\temp.json")
    #dfListTest = train.transform("C:\\Main\\Code\\ml-app\\temp.json")
    df = dfList[userOrder[client_id]]
    dfTest = dfListTest[client_id]
    #df = dfList[client_id]

    X = df.drop(columns=['label'])
    X = X.drop(columns=['pressureMedian'])
    X = X.drop(columns=['startX'])
    X = X.drop(columns=['startY'])
    X = X.drop(columns=['endX'])
    X = X.drop(columns=['endY'])

    X = X.drop(columns=['MXmax'])
    X = X.drop(columns=['MXmin'])
    X = X.drop(columns=['MXmean'])
    X = X.drop(columns=['MXmedian'])
    X = X.drop(columns=['MXSD'])
    X = X.drop(columns=['MYmax'])
    X = X.drop(columns=['MYmin'])
    X = X.drop(columns=['MYmean'])
    X = X.drop(columns=['MYmedian'])
    X = X.drop(columns=['MYSD'])
    X = X.drop(columns=['MZmax'])
    X = X.drop(columns=['MZmin'])
    X = X.drop(columns=['MZmean'])
    X = X.drop(columns=['MZmedian'])
    X = X.drop(columns=['MZSD'])
    y = df['label']

    #'''
    X1 = dfTest.drop(columns=['label'])
    X1 = X1.drop(columns=['pressureMedian'])
    X1 = X1.drop(columns=['startX'])
    X1 = X1.drop(columns=['startY'])
    X1 = X1.drop(columns=['endX'])
    X1 = X1.drop(columns=['endY'])

    X1 = X1.drop(columns=['MXmax'])
    X1 = X1.drop(columns=['MXmin'])
    X1 = X1.drop(columns=['MXmean'])
    X1 = X1.drop(columns=['MXmedian'])
    X1 = X1.drop(columns=['MXSD'])
    X1 = X1.drop(columns=['MYmax'])
    X1 = X1.drop(columns=['MYmin'])
    X1 = X1.drop(columns=['MYmean'])
    X1 = X1.drop(columns=['MYmedian'])
    X1 = X1.drop(columns=['MYSD'])
    X1 = X1.drop(columns=['MZmax'])
    X1 = X1.drop(columns=['MZmin'])
    X1 = X1.drop(columns=['MZmean'])
    X1 = X1.drop(columns=['MZmedian'])
    X1 = X1.drop(columns=['MZSD'])
    y1 = dfTest['label']
    #'''

    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2, random_state=42, stratify=y)
    return X_train, y_train, X1.astype(np.float32).to_dict('split')['data'], y1 # this line of code is to return the temp.json as test dataset
    #return X_train, y_train, X_test, y_test # this line of code is to return the normal train_test_split as training and testing dataset

# Look at the RandomForestClassifier documentation of sklearn and select the parameters
# Get the parameters from the RandomForestClassifier
def get_params(model: RandomForestClassifier) -> List[np.ndarray]:
    params = [
        model.n_estimators,
        model.max_depth,
        model.min_samples_split,
        model.min_samples_leaf,
    ]
    return params


# Set the parameters in the RandomForestClassifier
def set_params(model: RandomForestClassifier, params: List[np.ndarray]) -> RandomForestClassifier:
    model.n_estimators = int(params[0])
    model.max_depth = int(params[1])
    model.min_samples_split = int(params[2])
    model.min_samples_leaf = int(params[3])
    return model