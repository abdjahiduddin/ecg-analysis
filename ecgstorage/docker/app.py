import json
import pymongo

# Flask utils
from flask import Flask,  jsonify
from gevent.pywsgi import WSGIServer

app = Flask("ECG Arrhytmia Storage")

client = pymongo.MongoClient("mongodb://10.103.99.192:27017/")
db = client["ecgarrhytmia"]

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
        lenData = data["len"]
        ecg = data["data"]
        hasil = hasil["hasil"] 

        tmp = {
            "status":"OK",
            "result":{
                "nama":nama,
                "umur":umur,
                "len":lenData,
                "data":ecg,
                "hasil":hasil
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
    # app.run(port=5001, debug=True)
    try:
        print("Start Serving ECG Storage......")
        print("Running on http://127.0.0.1:5001")
        print("Quit the server with CTRL-C")
	    # Serve the app with Gevent
        http_server = WSGIServer(('', 5001), app)
        http_server.serve_forever()
    except KeyboardInterrupt:
        print("-------------------------------------------")
        print("Shutting Down Server http://127.0.0.1:5000")
        print("Bye.")
        print("-------------------------------------------")
