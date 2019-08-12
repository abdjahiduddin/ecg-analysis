import csv
import requests
import json
import time

url = "http://api.iotapps.belajardisini.com/topic/dataecg"


with open('/home/jay/Documents/analysis-infrastructure/ecgclasify/datasets/105-V1.csv', 'r') as csvFile:
    reader = csv.reader(csvFile)
    i = 0
    
    for row in reader:
        if i > 0:
            iot = {
                'Nama':"Doe",
                'Umur':45,
                'Detak Jantung':float(row[0])
            }
            r = requests.post(url, data = { 
                'data': json.dumps(iot) 
            },headers = {
                 'Authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwOlwvXC9hcGkuaW90YXBwcy5iZWxhamFyZGlzaW5pLmNvbVwvdXNlclwvbG9naW4iLCJpYXQiOjE1NjU0MzY4MjIsIm5iZiI6MTU2NTQzNjgyMiwianRpIjoicXdKZVJBZng3eVdwVE8wUCIsInN1YiI6IjVjYmQ4ZmY3YWRiMDY0M2NlMDc5ZTQ2NCIsInBydiI6Ijg3ZTBhZjFlZjlmZDE1ODEyZmRlYzk3MTUzYTE0ZTBiMDQ3NTQ2YWEiLCJkZXZpY2UiOiI1Y2JkOTQ1MWFkYjA2NDNjZTE2ZGEzOTIifQ.7cb9tYxgfe2_LhC1zm_mkyPMnv5g-qk44r81k6rjn3M"
            })
            
            if(r.status_code==200):
                print("Sending Data : ",r.content)
        i = i+1
        #time.sleep(6)
        
        

csvFile.close()
