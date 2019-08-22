from pymongo import MongoClient

# Connect to MongoDB (raw collection)
client = MongoClient('mongodb://127.0.0.1')
database = client.heart_rate
connections = {}
connections["raw"] = database.raw
print("[MongoDB] Connected to Collection: Raw")
connections["user"] = database.user
print("[MongoDB] Connected to Collection: User")
connections["trend"] = database.trend
print("[MongoDB] Connected to Collection: Trend")
connections["dataset"] = database.dataset
print("[MongoDB] Connected to Collection: Dataset")
connections["test"] = database.test
print("[MongoDB] Connected to Collection: Test")
connections["conclusion"] = database.conclusion
print("[MongoDB] Connected to Collection: Conclusion")