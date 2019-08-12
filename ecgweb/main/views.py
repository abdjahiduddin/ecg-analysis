from django.shortcuts import render
from django.http import HttpResponse
import requests
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from pylab import figure, axes, pie, title, show
from matplotlib import pyplot as plt

from .ecglib import ecg


def homepage(response):
    urlStorage = "http://127.0.0.1:5001/getAllName"
    urlAnalytic = "http://127.0.0.1:5000/"
    responAnalytic = requests.request("GET", urlAnalytic)
    responAnalytic = responAnalytic.json()
    if responAnalytic['status'] == "OK":
        args = {}
        responStorage = requests.request("GET", urlStorage)
        respon = responStorage.json()
        args['data'] = respon
        return render(response,"main/index.html",args)
    else:
        return render(response,"main/404.html")

def analytic(response, username):
    urlAnalytic = "http://127.0.0.1:5000/requestAnalysis/{}".format(username)
    responAnalytic = requests.request("GET", urlAnalytic)
    responAnalytic = responAnalytic.json()
    if responAnalytic['status'] == "OK":
        args = getHasil(username)
        return render(response,"main/details.html",args)
    else:
        return render(response,"main/404.html")


def getHasil(username):
    args = {}
    url = "http://127.0.0.1:5001/getOneData/{}".format(username)
    respon = requests.request("GET", url)
    result = respon.json()
    
    args['data'] = result['result']['data']
    args['filtered'] = result['result']['filtered']
    args['hasil'] = result['result']['hasil']
    print(args['hasil'])
    args['hr'] = result['result']['hr']
    args['hr_template'] = result['result']['hr_template']
    args['rpeaks'] = result['result']['rpeaks']
    args['nama'] = result['result']['nama'] 
    args['umur'] = result['result']['umur']
    
    return args


