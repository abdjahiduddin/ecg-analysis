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
        args = getImage(username)
        return render(response,"main/details.html",args)
    else:
        return render(response,"main/404.html")


def getImage(username):
    args = {}
    url = "http://127.0.0.1:5001/getOneData/{}".format(username)
    respon = requests.request("GET", url)
    result = respon.json()
    data = result['result']['data']
    # Will Show in Template
    PVC = []
    PAB = []
    RBB = []
    LBB = []
    APC = []
    VEB = []

    args['nama'] = result['result']['nama'] 
    args['umur'] = result['result']['umur']
    args['summary'] = imgToBuffer(data)

    hasil = result['result']['hasil']

    if len(hasil['PVC']) > 0:
        for x in hasil['PVC']:
            imgBase = dataToImgBuffer(data,x[0],x[1])
            PVC.append([x[0],x[1],imgBase])

    if len(hasil['PAB']) > 0:
        for x in hasil['PAB']:
            imgBase = dataToImgBuffer(data,x[0],x[1])
            PAB.append([x[0],x[1],imgBase])

    if len(hasil['RBB']) > 0:
        for x in hasil['RBB']:
            imgBase = dataToImgBuffer(data,x[0],x[1])
            RBB.append([x[0],x[1],imgBase])

    if len(hasil['LBB']) > 0:
        for x in hasil['LBB']:
            imgBase = dataToImgBuffer(data,x[0],x[1])
            LBB.append([x[0],x[1],imgBase])

    if len(hasil['APC']) > 0:
        for x in hasil['APC']:
            imgBase = dataToImgBuffer(data,x[0],x[1])
            APC.append([x[0],x[1],imgBase])

    if len(hasil['VEB']) > 0:
        for x in hasil['VEB']:
            imgBase = dataToImgBuffer(data,x[0],x[1])
            VEB.append([x[0],x[1],imgBase])
    
    args['PVC'] = PVC
    args['PAB'] = PAB
    args['RBB'] = RBB
    args['LBB'] = LBB
    args['APC'] = APC
    args['VEB'] = VEB

    return args


def imgToBuffer(data):
    out = ecg.ecg(signal=data, sampling_rate=200., show=True)
    buf = BytesIO()
    out.savefig(buf, format='png', dpi=300)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    return image_base64

def dataToImgBuffer(data,x,y):
    i = data[x:y]
    fig = plt.figure(frameon=False)
    plt.plot(i) 
    plt.xticks([]), plt.yticks([])
    for spine in plt.gca().spines.values():
        spine.set_visible(False)

    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8').replace('\n', '')
    buf.close()
    return image_base64

