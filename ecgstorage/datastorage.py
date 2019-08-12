import json
import pymongo
import numpy as np

# Flask utils
from flask import Flask,  jsonify, request
from gevent.pywsgi import WSGIServer

app = Flask("ECG Arrhytmia Storage")

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["arrhytmia"]

@app.route('/getAllName', methods=['GET'])
def getAllPasienName():
    data = []
    col = db["pasien"]
    pasien = col.find({})
    for i in pasien:
        tmp = {
            "nama":i["nama"],
            "umur":i["umur"]
        }
        data.append(tmp)
    payload = jsonify(data)
    return payload

@app.route('/getOneData/<string:name>', methods=['GET'])
def getOnePasienData(name):
    errorMsg = ""
    count = 0
    
    col = db["data"]
    col1 = db["pasien"]
    col2 = db["hasil"]

    check = []


    check.append(col.find({"nama":name}).count())
    check.append(col1.find({"nama":name}).count())
    check.append(col2.find({"nama":name}).count())
    if check.count(1) < 3:
        for count,i in enumerate(check):
            if i == 0:
                if count == 0:
                    errorMsg = errorMsg + " Data in Data Collection Not Found."
                elif count == 1:
                    errorMsg = errorMsg + " Data in Pasien Collection Not Found."
                else:
                    errorMsg = errorMsg + " Data in Hasil Collection Not Found."
        tmp = {
            "status":"ERROR",
            "message":errorMsg
        }

    else:
        data = col.find_one({"nama":name})
        pasien = col1.find_one({"nama":name})
        hasil = col2.find_one({"nama":name})

        nama = name
        umur = pasien["umur"]
        ecg = data["data"]
        ts = data["timeseries"]
        ecg_ts = []
        # ts + ecg
        for count,i in enumerate(ecg):
            ecg_ts.append([ts[count],i])

        filtered = data["filtered"]
        filtered_ts = []
        # ts + filtered
        for count,i in enumerate(filtered):
            filtered_ts.append([ts[count],i])

        # hasil
        result = hasil["hasil"]
        PVC = []
        PAB = []
        RBB = []
        LBB = []
        APC = []
        VEB = []
        for key in result.keys():
            if len(result[key]) > 0 :
                tmp = result[key]
                for x in tmp:
                    if key == "PVC":
                        PVC.append([ts[x[0]],ts[x[1]]])
                    elif key == "PAB":
                        PAB.append([ts[x[0]],ts[x[1]]])
                    elif key == "RBB":
                        RBB.append([ts[x[0]],ts[x[1]]])
                    elif key == "LBB":
                        LBB.append([ts[x[0]],ts[x[1]]])
                    elif key == "APC":
                        APC.append([ts[x[0]],ts[x[1]]])
                    elif key == "VEB":
                        VEB.append([ts[x[0]],ts[x[1]]])
        result = {
            "APC": APC, 
            "LBB": LBB, 
            "PAB": PAB, 
            "PVC": PVC, 
            "RBB": RBB, 
            "VEB": VEB
            }

        #get value ts by rpeaks index
        rpeaks = hasil["rpeaks"]
        rpeaks = np.array(rpeaks)
        ts_tmp = np.array(ts)
        rpeaks = ts_tmp[rpeaks]
        rpeaks = rpeaks.tolist()

        hr = hasil["heart_rate"]
        hr_template = hasil["hr_template"]

        tmp = {
            "status":"OK",
            "result":{
                "nama":nama,
                "umur":umur,
                "data":ecg_ts,
                "hasil":result,
                "filtered":filtered_ts,
                "hr_template":hr_template,
                "rpeaks": rpeaks,
                "hr":hr
            }
        }

    payload = jsonify(tmp)
    return payload

@app.route('/insertNama', methods=['POST'])
def insert_nama():
    col = db["pasien"]
    msg = "OK"
    try:
        name = request.json['nama']
        umur = request.json['umur']
        col.insert_one({'nama':name,'umur':umur}) 
    except:
        msg = "ERROR, INSERT HASIL, DB-API"
    return msg

@app.route('/insertData', methods=['POST'])
def insert_data():
    col = db["data"]
    msg = "OK"
    try:
        data = request.json['data']
        col.insert_one(data)
    except:
        msg = "ERROR, INSERT HASIL, DB-API"
    return msg

@app.route('/insertHasil', methods=['POST'])
def insert_hasil():
    col = db["hasil"]
    msg = "OK"
    try:
        hasil = request.json['hasil']
        col.insert(hasil)
    except:
        msg = "ERROR, INSERT HASIL, DB-API"
    return msg

if __name__ == '__main__':
    # app.run(port=5000, debug=True)
    try:
        print("Start Serving ECG Storage......")
        # Serve the app with gevent
        http_server = WSGIServer(('', 5001), app)
        print("Running on http://127.0.0.1:5001")
        print("Quit the server with CTRL-C")
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("-------------------------------------------")
        print("Shutting Down Server http://127.0.0.1:5000")
        print("Bye.")
        print("-------------------------------------------")
