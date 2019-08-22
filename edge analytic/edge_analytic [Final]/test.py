import random
from datetime import datetime
from mongodb import connections


# Create test case
def create_case():
    variant = {
        "profile": [],
        "activity": [0, 1],
        "hr_range": [20, 180]
    }

    except_admin = {"username": {"$ne": "admin"}}
    fields = {
        "_id": 0,
        "username": 1,
        "age": 1,
        "device": 1
    }

    for user in connections["user"].find(except_admin, fields):
        variant["profile"].append(user)

    total_data = int(raw_input("Case> "))

    for loop in range(0, total_data):
        new_data = random.choice(variant["profile"])
        new_data["activity"] = random.choice(variant["activity"])
        new_data["heart_rate"] = random.randint(variant["hr_range"][0], variant["hr_range"][1])
        new_data["time"] = datetime.now()
        new_data["processed"] = False
        connections["raw"].insert_one(new_data)
        print(new_data)
        del new_data["id"]


# Save resource as test attribute
# Resource = pid, create_time, cpu percent, memory percent, disk read, disk write
def resource(attribute, value):
    result = {
        "attribute": attribute,
        "value": value,
        "time": datetime.now()
    }
    connections["test"].insert_one(result)


# Save runtime as test attribute
def runtime(info):
    result = {
        "attribute": "runtime (" + info + ")",
        "time": datetime.now()
    }
    connections["test"].insert_one(result)


# Save the converted test attributes to test conclusion
def conclude():
    test_result = {}
    test_result["case"] = int(input("How many data? (case) > "))
    test_result["pid"] = connections["test"].find_one({"attribute": "pid"})["value"]
    test_result["create_time"] = connections["test"].find_one({"attribute": "create_time"})["value"]

    runtime = {}
    for attr in ["start", "end"]:
        temp = []
        for log in connections["test"].find({"attribute": "runtime (" + attr + ")"}):
            temp.append(log["time"])
        if attr == "start":
            runtime["start"] = min(temp)
        else:
            runtime["end"] = max(temp)

    runtime["total"] = (runtime["end"] - runtime["start"]).total_seconds()
    test_result["runtime"] = runtime

    attribute_list = [
        "cpu_percent",
        "memory_percent",
        "disk_read",
        "disk_write"
    ]

    time_range = {
        "$gte": runtime["start"],
        "$lte": runtime["end"]
    }

    for attr in attribute_list:
        test_result[attr] = {}
        test_result[attr]["data"] = []
        for data in connections["test"].find({"attribute": attr, "time": time_range}):
            test_result[attr]["data"].append(data["value"])
        test_result[attr]["average"] = round(sum(test_result[attr]["data"]) / len(test_result[attr]["data"]), 1)

    connections["test"].delete_many({})
    connections["conclusion"].insert_one(test_result)
