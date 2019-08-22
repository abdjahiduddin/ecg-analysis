import jwt
from pymongo import MongoClient
import json
import datetime
client = MongoClient('mongodb://127.0.0.1:27017')
secretKey = "Ki6wt83A5txZCX0FV0gbtuDazhhgFwd4"

def validate_token(request):

    if not request or 'Bearer' not in request:
        return False

    split = request.split(' ')
    dbadmin = client.admin
    decode_data = jwt.decode(split[1], secretKey, algorithms=['HS256'])
    validate = dbadmin['authUser'].find_one({"name": decode_data['username'], "mac": decode_data['mac']}, {"_id" : 1})
    
    if(validate == None):
        return False
    else:
        return True


@csrf_exempt
def postData(request):
    if request.method == 'POST':
        token = request.headers.get('Authorization')
        if(validate_token(token)):
            pureToken = token.split(' ')
            datas =json.loads(request.body)
            datajson = json.loads(datas)
            return dataPost(datas, datajson['topic'], pureToken[1]) 
    return HttpResponse('/api/post')

def validate_topic(topic, token):
    db = client.admin
    topics = db["topics"]
    validate = topics.find_one({"name": topic, 'jwt_token': token}, {"_id" : 1})
    if (validate):
        return True
    else:
        return False

def checkFormat(data):
    dict1 = json.loads(data)
    dict2 = dict1['payload']
    for r in dict2:
        if 'files' in r:
            return 'file'
        else:
            return 'json'

def isCompatible(formats, structure):
    if(structure=="structured") and (formats == "json"):
        return True
    elif(structure=="unstructured") and (formats == "file" or formats == "raw" or formats == "json"):
        return True
    else:
        return False

def synchronizeSizeEntry(dateTopic, datenow):
    db = client['admin']
    mycolDate = db[dateTopic]
    check = mycolDate.find({"date": datenow}).distinct("entry")[0]
    if check == 0:
        mycolDate.update({"date": datenow}, {"$set": {'entry': 1}})
    else:
        getCount = mycolDate.find({'date': datenow}).distinct("entry")
        totalEntrty = getCount[0] + 1
        mycolDate.update({'date': datenow}, {"$set": {"entry": totalEntrty}})

def dataPost(datas, topic, token):
    topics = topic.split('/')[1]
    if(validate_topic(topics, token)):
        dbadmin = client.admin

        getStructure = dbadmin['topics'].find({"name": topics}).distinct("structure")[0].encode("ascii","replace")
        strGetStructure = getStructure.decode('utf-8')
        formats = checkFormat(datas)

        if not isCompatible(formats, strGetStructure):
            return HttpResponse('error : format and structure is not compatible')
        
        id_user = dbadmin['topics'].find({'name': topics}).distinct("user_id")[0]
        a = str(id_user)
        database_name = dbadmin['authUser'].find({"_id": ObjectId(id_user)}).distinct("database_name")[0].encode("ascii","replace")
        db_decode = database_name.decode('utf-8')
        namedb = str(db_decode)
        db = client[namedb]

        dateTopic = dbadmin['date'+topics]
        datenow = datetime.datetime.now()
        checkDate = dateTopic.find_one({"date": datenow}, {"_id" : 1})

        if(formats == "json"):
            if checkDate is None:
                dateTopic.insert({"date" : datenow, "entry" : 0})
            mycol = db[topics]
            dataloads = json.loads(datas)
            mycol.insert(dataloads)
            mycolDate = 'date'+topics
            synchronizeSizeEntry(mycolDate, datenow)
            return HttpResponse("sys JSON data saved in MongoDB")
        elif(formats == "file"):
            data1 = json.loads(datas)
            dict2 = data1['payload']
            raw = []
            if("files" in datas):
                raw.append(data1['payload']['files'])
            elif('payload' in datas):
                raw.append(data1['payload'])
            sizes = len(raw[0])
            print("size = ", sizes)
            if(sizes > 100):
                r = requests.post(
                    "http://127.0.0.1:5000/api/file_rules1", 
                    json = json.dumps(data1), 
                    headers = {
                        'Content-type': 'application/json; charset=UTF-8',
                        'Authorization': "Bearer {}".format(token)}
                    )
                return HttpResponse("sys FILE data saved in Directory")
            else:
                print("masuk else file")
                mycolDate = 'date'+topics
                synchronizeSizeEntry(mycolDate, datenow)

                return HttpResponse("sys FILE data saved in MongoDB")
    else:
        return HttpResponse("error : Wrong topic or topic is unregistered")
