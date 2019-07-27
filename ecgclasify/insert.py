import pymongo
import csv

def insertNama():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["testing"]
    col = db["pasien"]
    # names = [{'nama': 'jay', 'umur': 22, 'len': 3600},{'nama': 'john', 'umur': 40, 'len': 3600}]
    # for x in names:
    #     name = x['nama']
    #     umur = x['umur']
    col.insert_one({
        'nama':"dummy",
        'umur':999
    }) 

def insertData():
    # with open('100.csv', 'r') as csvFile:
    #     reader = csv.reader(csvFile)
    #     i = 0
    #     data = []

    #     for row in reader:
    #         if i > 0:
    #             data.append(float(row[0]))
    #         i = i+1
    iot = {
        "nama":"dummy",
        "data":"dummy",
        "len":999999
    }
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["testing"]
    col = db["data"]
    col.insert_one(iot)
    # csvFile.close()

def insertHasil():
    pred = {
        'APC': [[1927, 2224]], 
        'Normal': [[223, 517], [516, 805], [805, 1089], [1089, 1373], [1373, 1662], [1662, 1927], [2224, 2555], [2554, 2852], [2852, 3141], [3140, 3422]], 
        'LBB': [], 
        'PAB': [], 
        'PVC': [], 
        'RBB': [], 
        'VEB': []}
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["testing"]
    col = db["hasil"]
    print(pred["Normal"])
    col.insert_one(
        {
            "nama": "dummy",
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
    )

def findData():
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["test"]
    col = db["hasil"]
    x = col.find({ "nama": "" }).count()
    print(x)


insertNama()