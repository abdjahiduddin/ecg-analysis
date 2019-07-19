import requests
import numpy as np
import pandas as pd
import pymongo
import json

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["testing"]

def getAllData():
    #GET ALL RECORD FROM CLOUD
    urlLen = "http://api.iotapps.belajardisini.com/topic/dataecg/limit/1000000"
    headers = {
        'Authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9hcGkuaW90YXBwcy5iZWxhamFyZGlzaW5pLmNvbVwvdXNlclwvbG9naW4iLCJpYXQiOjE1NTU5NDQ2NTksIm5iZiI6MTU1NTk0NDY1OSwianRpIjoiOHZoWUtxdlh5WDh6R21sTCIsInN1YiI6IjVjYmQ4ZmY3YWRiMDY0M2NlMDc5ZTQ2NCIsInBydiI6Ijg3ZTBhZjFlZjlmZDE1ODEyZmRlYzk3MTUzYTE0ZTBiMDQ3NTQ2YWEiLCJkZXZpY2UiOiI1Y2JkOTQ1MWFkYjA2NDNjZTE2ZGEzOTIifQ.NRkT8UAEWzSk2ZfkFZAySqF7QsfCss5dH_Fh3vUBH94"
    }

    responseLen = requests.request("GET", urlLen, data={}, headers=headers)

    dataCloud = json.loads(responseLen.text)
    dataCloud = dataCloud['data']

    return dataCloud


def getNameLenData(df):
    #GET NAME LENGTH DATA

    #count data len by name
    dataCount = df.groupby('Nama', as_index=False).count()
    dataCount = dataCount.rename(columns={'Umur':'len'})
    dataCount = dataCount.loc[:,['Nama','len']]

    #convert to json
    lenData = dataCount.to_json(orient='records')
    
    lenData = json.loads(lenData)
    pasien = []
    for x in lenData:
        tmp = df[df['Nama'] == x['Nama']]
        tmp = tmp.loc[:,['Nama','Umur']]
        tmp = tmp.iloc[0]
        tmp = {
            'nama':x['Nama'],
            'umur':tmp['Umur'],
            'len':x['len']
        }
        pasien.append(tmp)

    return pasien


def splitData(df,lenData):
    datas = []
    for i in lenData:
        name = df['Nama'] == i['nama']
        data = df[name]
        data = data.loc[:,'Detak Jantung']
        data = data.values.tolist()
        datas.append(data)
    return datas


def preprocessing(state):
    names = ""
    datas = ""
    allData = getAllData()

    #convert data cloud to pandas dataframe
    df = pd.DataFrame(allData)

    #get data from dataframe
    data = df.loc[:,'data']
    
    #convert to json
    datajson = data.to_json(orient='records')
    dtJson = json.loads(datajson)

    #data cloud json convert to dataframe
    df2 = pd.DataFrame(dtJson)

    if state == "home":
        names = getNameLenData(df2)
        datas = splitData(df2,names)
    else:
        names = state
        name = df2['Nama'] == state
        data = df2[name]
        data = data.loc[:,'Detak Jantung']
        datas = data.values.tolist()
    return names, datas

col = db["data"]
dataJay = col.find_one({"nama":"jay"})
dataJay = dataJay["data"]
dataJohn = col.find_one({"nama":"john"})
dataJohn = dataJohn["data"]

names, datas = preprocessing("home")
dataJayCloud = datas[0]
dataJohnCloud = datas[1]
checkDataJay = []
checkDataJohn = []

for count, i in enumerate(dataJayCloud):
    if i == dataJay[count]:
        checkDataJay.append(True)
    else:
        checkDataJay.append(False)

for count, i in enumerate(dataJohnCloud):
    if i == dataJohn[count]:
        checkDataJohn.append(True)
    else:
        checkDataJohn.append(False)
print("------------------------------------")
for count,i in enumerate(checkDataJay):
    if i == False:
        print("No : ",count)
print("------------------------------------")
for count,i in enumerate(checkDataJohn):
    if i == False:
        print("No : ",count)
