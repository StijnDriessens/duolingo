import os
from pymongo import MongoClient

username = os.getenv('MONGO_USERNAME')
password = os.getenv('MONGO_PASSWORD')

# Replace with your MongoDB Atlas connection string
uri = "mongodb+srv://{username}:{password}@duolingo.ijztv.mongodb.net/Duolingo?retryWrites=true&w=majority&appName=Duolingo"

# Create a client and try to connect
try:
    client = MongoClient(uri)
    # Access the database
    db = client.Duolingo  # Use the database you want to connect to
    # Access a collection in the database
    collection = db.Duolingo  # Replace with your collection name

    # Insert a record to test the connection
    record = {
        "name": "Felix",
        "dayStreak": 400,
        "totalXP": 4000,
        "league": "Ruby Week 2",
        "top3Finishes": 4,
        "course": "Dutch",
        "courseXP": 300
    }
    result = collection.insert_one(record)
    print(f"Inserted document with _id: {result.inserted_id}")

except ConnectionError as e:
    print(f"Error connecting to MongoDB: {e}")
