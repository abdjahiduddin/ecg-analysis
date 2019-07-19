import json
import requests

urlStorageGetAll = "http://127.0.0.1:5001/getAllName"
urlStorageGetOneData = "http://127.0.0.1:5001/getOneData/Alex"
url = "http://127.0.0.1:5000/"
urlAnalytic = "http://127.0.0.1:5000/requestAnalysis/Alex"

payload = ""
headers = {
    'cache-control': "no-cache"
    }

print("Accessing Home - Calling Analytic")
response = requests.request("GET", url, data=payload, headers=headers)
print("Result")
print(response.text)
print("-----------------------------------")

print("Accessing Home - Calling Storage")
response = requests.request("GET", urlStorageGetAll, data=payload, headers=headers)
print("Result")
print(response.text)
print("-----------------------------------")

print("Accessing Request Analytic - Calling Analytic")
response = requests.request("GET", urlAnalytic, data=payload, headers=headers)
print("Result")
print(response.text)
print("-----------------------------------")

print("Accessing Request Analytic - Calling Storage")
response = requests.request("GET", urlStorageGetOneData, data=payload, headers=headers)
print("Result")
print(response.text)
print("-----------------------------------")
