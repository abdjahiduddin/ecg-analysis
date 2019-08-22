import os
import re
import time
import json

# Specify API folder
api_folder = os.getcwd() + "/static/api/"


# Change datetime to timestamp (Python v2 doesn't have timestamp attribute)
def timestamp(trend_time):
    return int((time.mktime(trend_time.timetuple())+trend_time.microsecond/1000000))


# Create track trend file
def create_file(new_trend):
    # Remove Id
    new_trend.pop("_id")
    # Change timestamp to datetime
    new_trend["trend"]["time"] = timestamp(new_trend["trend"]["time"])
    # Define filename by device's MAC address
    filename = new_trend["profile"]["username"] + "_" + re.sub(":", "", new_trend["profile"]["device"]) + ".json"
    with open(api_folder + filename, 'w') as file:
        json.dump(new_trend, file)
    print("[API] Trend Type Track Saved to File " + filename)
