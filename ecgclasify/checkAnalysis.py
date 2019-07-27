from __future__ import division, print_function
# coding=utf-8
import sys
import os
import glob
import re
import numpy as np
import cv2
import pandas as pd
import numpy as np
import biosppy
import matplotlib.pyplot as plt
from biosppy.signals import ecg
    

#pymongo
import pymongo

#Library for get data from cloud
import json
import requests
import csv

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image


# Load your trained model
model = load_model('/home/jay/Documents/Model/ecgScratchEpoch2.hdf5')
model._make_predict_function()          # Necessary
print('Model loaded. Start serving...')
output = []


def model_predict(uploaded_files, model):
    
    flag = 1
    
    #index1 = str(path).find('sig-2') + 6
    #index2 = -4
    #ts = int(str(path)[index1:index2])
    APC, NORMAL, LBB, PVC, PAB, RBB, VEB = [], [], [], [], [], [], []
    result = {"APC": APC, "Normal": NORMAL, "LBB": LBB, "PAB": PAB, "PVC": PVC, "RBB": RBB, "VEB": VEB}
        
    kernel = np.ones((4,4),np.uint8)
    indices = []
    signals = []
    count = 1
    peaks =  biosppy.signals.ecg.christov_segmenter(signal=uploaded_files, sampling_rate = 200.)[0]
    for i in (peaks[1:-1]):
        diff1 = abs(peaks[count - 1] - i)
        diff2 = abs(peaks[count + 1]- i)
        x = peaks[count - 1] + diff1//2
        y = peaks[count + 1] - diff2//2
        signal = data[x:y]
        signals.append(signal)
        count += 1
        ranges = [x.item(),y.item()]
        indices.append(ranges)
        
    for count, i in enumerate(signals):
        fig = plt.figure(frameon=False)
        plt.plot(i) 
        plt.xticks([]), plt.yticks([])
        for spine in plt.gca().spines.values():
            spine.set_visible(False)

        filename = 'fig' + '.png'
        fig.savefig(filename)
        im_gray = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        im_gray = cv2.erode(im_gray,kernel,iterations = 1)
        im_gray = cv2.resize(im_gray, (128, 128), interpolation = cv2.INTER_LANCZOS4)
        cv2.imwrite(filename, im_gray)
        im_gray = cv2.imread(filename)
        pred = model.predict(im_gray.reshape((1, 128, 128, 3)))
        pred_class = pred.argmax(axis=-1)
        if pred_class == 0:
            APC.append(indices[count]) 
        elif pred_class == 1:
            NORMAL.append(indices[count]) 
        elif pred_class == 2:    
            LBB.append(indices[count])
        elif pred_class == 3:
            PAB.append(indices[count])
        elif pred_class == 4:
            PVC.append(indices[count])
        elif pred_class == 5:
            RBB.append(indices[count]) 
        elif pred_class == 6:
            VEB.append(indices[count])

#     result = sorted(result.items(), key = lambda y: len(y[1]))[::-1]   
#     output.append(result)
#     print(output)
#     data = {}
#     data['result'+str(flag)] = str(result)
#     print(data)

#     json_filename = 'data.txt'
#     with open(json_filename, 'a+') as outfile:
#         json.dump(data, outfile) 
#     flag+=1 
    

#     with open(json_filename, 'r') as file:
#         filedata = file.read()
#     filedata = filedata.replace('}{', ',')
#     with open(json_filename, 'w') as file:
#         file.write(filedata) 
    os.remove('fig.png')      
    return result
    


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



def requestAnalysis(nama):
    respon = "OK"
    try: 
        msg, status = checkInStorage(nama,"hasil")
        if msg == "OK":
            if status[0]["status"] == False:
                print("Starting Clasify.....")
                name, data = preprocessing(nama)
                pred = model_predict(data, model)
                msg = insertHasil(pred,nama)
                print("Clasify Done...")
        else:
            respon = "Something Wrong!! When Checking Data in Storage"
    except:
        respon = "ERROR Request Analysis"
    return respon


if __name__ == '__main__':
    # names, datas = preprocessing("home")
    csv = pd.read_csv("datasets/ipvc.csv")
    csv_data = csv[' Sample Value']
    data = np.array(csv_data)
    pred = model_predict(data, model)
    print(pred)
    out = ecg.ecg(signal=data, sampling_rate=200., show=True)


