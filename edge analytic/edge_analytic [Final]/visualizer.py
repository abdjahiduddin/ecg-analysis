import calendar
import matplotlib
import numpy as np
from collections import OrderedDict
from mongodb import connections
from datetime import timedelta

# Change machine to Agg
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Initialize canvas width 10 inches and height 5 inches (best size for LDA web server)
plt.figure(figsize=(10, 5))


# Main visualization process to creating graph
def main_process(info):
    # Create
    info["trend"] = define_x_axis(info["trend"])

    # Get graph trends
    trends = get_graph_trends(info)

    # Create graph
    if trends:
        plot_data(info, trends)


def define_x_axis(trend):
    trend["x-axis"] = {}
    trend["x-axis"]["list"] = []
    if trend["type"] == "yearly":
        trend["x-axis"]["type"] = "monthly"
        trend["x-axis"]["label"] = "month"
        trend["x-axis"]["format"] = "%m"

        # Get list of 1 year trend time
        max_day = 0
        for month in range(0, 12):
            latest = trend["date"] + timedelta(days=max_day)
            trend["x-axis"]["list"].append(latest.strftime(trend["x-axis"]["format"]))
            max_day += calendar.monthrange(latest.year, latest.month)[1]
    elif trend["type"] == "monthly":
        trend["x-axis"]["type"] = "daily"
        trend["x-axis"]["label"] = "day"
        trend["x-axis"]["format"] = "%d"

        # Get list of 1 month trend time
        max_day = calendar.monthrange(trend["date"].year, trend["date"].month)[1]
        for day in range(0, max_day):
            latest = trend["date"] + timedelta(days=day)
            trend["x-axis"]["list"].append(latest.strftime(trend["x-axis"]["format"]))
    else:
        trend["x-axis"]["type"] = "hourly"
        trend["x-axis"]["label"] = "hour"
        trend["x-axis"]["format"] = "%H"

        # Get list of 1 day trend time
        for hour in range(0, 24):
            latest = trend["date"] + timedelta(hours=hour)
            trend["x-axis"]["list"].append(latest.strftime(trend["x-axis"]["format"]))

    # Generate time range
    trend["latest"] = latest

    # Return trend time and format
    return trend


# Get all x-axis trends in dictionary
def get_graph_trends(info):
    # Generate query to get all correspond trend
    find_graph_trends = {
        "profile.username": info["user"]["username"],
        "profile.device": info["user"]["device"],
        "trend.type": info["trend"]["x-axis"]["type"],
        "trend.activity": info["trend"]["act(num)"],
        "trend.time": {"$gte": info["trend"]["date"], "$lte": info["trend"]["latest"]}
    }

    trends = OrderedDict()
    for trend in connections["trend"].find(find_graph_trends, sort=[("trend.time", 1)]):
        trends[trend["trend"]["time"].strftime(info["trend"]["x-axis"]["format"])] = trend["trend"]["heart_rate"]["average"]
    return trends


# Plot Data
def plot_data(info, trends):
    # Plot divider (low and high)
    for divider in info["user"]["divider_range"][info["trend"]["act(str)"]].keys():
        plt.plot(info["trend"]["x-axis"]["list"], np.full(len(info["trend"]["x-axis"]["list"]), info["user"]["divider_range"][info["trend"]["act(str)"]][divider]), "r--")
    # Plot trend data by dict
    plt.plot(trends.keys(), trends.values(), 'o-')

    # Initialize graph label and title
    plt.ylabel("average " + info["trend"]["act(str)"] + " heart rate (beats/minute)")
    plt.xlabel(info["trend"]["x-axis"]["label"])
    plt.title("Trends of " + info["trend"]["act(str)"] + " heart rate in " + info["trend"]["date"].strftime(info["trend"]["date_format"]))

    # Save to corresponding folder
    plt.savefig("static/visual/" + info["user"]["username"] + "_" + info["trend"]["act(str)"] + ".svg")

    # Reset canvas
    plt.gcf().clear()
