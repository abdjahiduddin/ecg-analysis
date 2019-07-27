from __future__ import division, print_function
# coding=utf-8
import os
import numpy as np
import cv2
import pandas as pd
import biosppy
import matplotlib.pyplot as plt

#pymongo
import pymongo

#Library for get data from cloud
import json
import requests

# Keras
from keras.applications.imagenet_utils import preprocess_input, decode_predictions
from keras.models import load_model
from keras.preprocessing import image

# Flask utils
from flask import Flask ,jsonify
from gevent.pywsgi import WSGIServer


app = Flask("ECG Arrhytmia Classification")

# Model saved with Keras model.save()

# Load your trained model
model = load_model('/home/jay/Documents/Model/ecgScratchEpoch2.hdf5')
model._make_predict_function()          # Necessary
output = []

#Make Connection to Mongodb
client = pymongo.MongoClient("mongodb://0.0.0.0:27017/")
db = client["testing"]

def model_predict(uploaded_files, model):
    
    #index1 = str(path).find('sig-2') + 6
    #index2 = -4
    #ts = int(str(path)[index1:index2])
    APC, NORMAL, LBB, PVC, PAB, RBB, VEB = [], [], [], [], [], [], []
    result = {"APC": APC, "Normal": NORMAL, "LBB": LBB, "PAB": PAB, "PVC": PVC, "RBB": RBB, "VEB": VEB}
        
    kernel = np.ones((4,4),np.uint8)
        
    data = np.array(uploaded_files)
    indices = []
    signals = []
    count = 1
    peaks =  biosppy.signals.ecg.christov_segmenter(signal=data, sampling_rate = 200.)[0]
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

    os.remove('fig.png')      
    return result


def getAllData():
    #GET ALL RECORD FROM CLOUD
    urlLen = "http://api.iotapps.belajardisini.com/topic/dataecg/limit/1000000000"
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


def checkInStorage(names,collection):
    msg = "OK"
    try:
        namesStatus = []
        status = False
        col = db[collection]
        # Check Name Pasien Exist Or Not
        if collection == "pasien":
            for i in names:
                x = col.find({ "nama": i["nama"] }).count()
                if x == 1:
                    status = True
                namesStatus.append({
                    "nama": i["nama"],
                    "status": status
                })
        # Check Clasify Result Exist Or Not
        elif collection == "hasil":
            hasil = ""
            x = col.find({"nama":names}).count()
            if x == 1:
                data = col.find_one({"nama":names})
                status = True
                hasil = data["hasil"]
            namesStatus.append({
                "nama": names,
                "status": status,
                "hasil": hasil
            })
    except:
        msg = "ERROR, CHECK DATA IN STORAGE"
    return msg,namesStatus


def insertNama(names):
    msg = "OK"
    try:
        col = db["pasien"]
        name = names['nama']
        umur = names['umur']
        umur = umur.item()
        col.insert_one({'nama':name,'umur':umur}) 
    except:
        msg = "ERROR, INSERT NAME"
    return msg
    

def insertData(data,name,len):
    msg = "OK"
    try:
        col = db["data"]
        iot = {
            "nama":name,
            "data":data,
            "len":len
        }
        
        col.insert_one(iot)
    except:
        msg = "ERROR, INSERT DATA"
    return msg
    

def insertHasil(pred,nama):
    msg = "OK"
    col = db["hasil"]
    try:
        hasil = {
                "nama": nama,
                "hasil": {
                    'APC': pred["APC"], 
                    'Normal': pred["Normal"], 
                    'LBB': pred["LBB"], 
                    'PAB': pred["PAB"], 
                    'PVC': pred["PVC"], 
                    'RBB': pred["RBB"], 
                    'VEB': pred["VEB"]
                }
            }
        col.insert_one(hasil)
    except:
        msg = "ERROR, INSERT HASIL"
    return msg

@app.route('/requestAnalysis/<string:nama>', methods=['GET'])
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
            respon = msg
    except:
        respon = "ERROR Request Analysis"
    respon = {
        'status': respon
    }
    respon = jsonify(respon)
    return respon

@app.route('/', methods=['GET'])
def showHome():
    respon = "OK"
    counter = 0
    try:
        names, datas = preprocessing("home")
        msg, status = checkInStorage(names,"pasien")
        print(msg)
        if msg == "OK":
            for counter,i in enumerate(status):
                if i["status"] == False:
                    print("Saving Pasien Name To Storage")
                    msg = insertNama(names[counter])
                    print("Saving Pasien Data To Storage")
                    msg = insertData(datas[counter],names[counter]['nama'],names[counter]['len'])
                    print("--------------------------------------------------------------------")
        else:
            respon = msg
    except :
        respon = "ERROR, Home"
    respon = {
        'status': respon
    }
    respon = jsonify(respon)
    return respon

if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    try:
        print("-------------------------------------------")
        print('Model loaded. Start serving ECG Analytic......')
        print("Running on http://127.0.0.1:5000")
        print("Quit the server with CTRL-C")
        # Serve the app with gevent
        http_server = WSGIServer(('', 5000), app)
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("-------------------------------------------")
        print("Shutting Down Server http://127.0.0.1:5000")
        print("Bye.")
        print("-------------------------------------------")

