from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["arthsaathi"]

users = db["users"]
conversations = db["conversations"]