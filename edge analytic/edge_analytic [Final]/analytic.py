from datetime import datetime
from bson.objectid import ObjectId
from heartrate_classifier import classify, main_process as generate_classifier
from mongodb import connections
from api import create_file
from test import runtime


# Main process for analytic component
# Listen to raw collection
def main_process():
    # Generate Heart Rate Classifier
    generate_classifier()

    try:
        print("[Analytic] Listened To Collection: Raw")
        while True:
            for raw in connections["raw"].find({"processed": False}).limit(10):
                print("[Analytic] Received:" + str(raw))

                ### TESTING ###
                #runtime("start")

                # Check trends
                check_trends(raw)

                # Update previous trend in database
                connections["raw"].update({"_id": ObjectId(raw['_id'])}, {"$set": {"processed": True}})
    except Exception as e:
        print("[Analytic] Exited" + str(e))
        exit(0)


# Create time series (by current time)
def create_series(time):
    time_range = {
        "track": time,
        "hourly": datetime(time.year, time.month, time.day, time.hour, 0, 0),
        "daily": datetime(time.year, time.month, time.day, 0, 0, 0),
        "monthly": datetime(time.year, time.month, 1, 0, 0, 0),
        "yearly": datetime(time.year, 1, 1, 0, 0, 0)
    }
    return time_range


# Check trends in database
def check_trends(new_data):
    # Define user information
    user = {
        "username": new_data["username"],
        "age": new_data["age"]
    }

    # Create time series trend
    time_range = create_series(new_data["time"])

    # For each time series trend
    for trend_type, time in time_range.items():
        # Current trend
        trend = {
            "type": trend_type,
            "activity": new_data["activity"],
            "time": time,
            "heart_rate": int(new_data["heart_rate"]),
            "device": new_data["device"]
        }

        # Check if trend exist
        check_trend = {
            "profile.username": new_data["username"],
            "profile.device": new_data["device"],
            "trend.type": trend_type,
            "trend.activity": new_data["activity"],
            "trend.time": time
        }
        trend_exist = connections["trend"].find_one(check_trend)

        # If trend exist
        if trend_exist:
            prev_trend = trend_exist
            update_trend(user, trend, prev_trend)
        else:
            create_trend(user, trend)

    ### TESTING ###
    #runtime("end")


# Create new trend
def create_trend(user, trend):
    # Constructing trend
    new_trend = {
        "trend": {
            "status": classify(trend["activity"], user["age"], trend["heart_rate"]),
            "type": trend["type"],
            "activity": trend["activity"],
            "time": trend["time"],
            "heart_rate": {
                "data": [trend["heart_rate"]],
                "average": trend["heart_rate"]
            }
        },
        "profile": {
            "device": trend["device"],
            "username": user["username"]
        }
    }

    # Insert new trend to database
    connections["trend"].insert_one(new_trend)
    print("[Analytic] " + str(new_trend) + " Inserted to Collection: Trend")

    # Save to file for trend_type track (API)
    if trend["type"] == "track":
        create_file(new_trend)


# Update previous trend
def update_trend(user, trend, prev_trend):
    # Recomputing average heart rate
    new_trend = prev_trend["trend"]["heart_rate"]
    new_trend["data"].append(trend["heart_rate"])
    new_trend["average"] = int(sum(new_trend["data"]) / len(new_trend["data"]))

    filter_trend = {
        "_id": ObjectId(prev_trend['_id'])
    }
    updated_trend = {
        "$set": {
            "trend.status": classify(prev_trend["trend"]["activity"], user["age"], new_trend["average"]),
            "trend.heart_rate.data": new_trend["data"],
            "trend.heart_rate.average": new_trend["average"]
        }
    }

    # Update previous trend in database
    connections["trend"].update(filter_trend, updated_trend)
    print("[Analytic] " + str(prev_trend["_id"]) + " Trend Updated in Collection: Trend")


if __name__ == "__main__":
    main_process()
