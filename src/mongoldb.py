from pymongo import MongoClient

client = MongoClient("mongodb://mongo:27017")
db = client["fitpic"]

def save_result(data):
    db.results.insert_one(data)
