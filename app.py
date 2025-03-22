from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

USERNAME = os.getenv("MONGO_USERNAME")
PASSWORD = os.getenv("MONGO_PASSWORD")
CLUSTER = os.getenv("MONGO_CLUSTER")
NAME = os.getenv("DUOLINGO_USERNAME")

uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER}.ijztv.mongodb.net/Duolingo?retryWrites=true&w=majority&appName=Duolingo"
client = MongoClient(uri)
db = client.get_database()  # This will use the default database set in the URI
collection = db.Duolingo  # Assuming 'Duolingo' is your collection name

@app.route('/')
def home():
    return "Welcome to the Duolingo API!"

@app.route('/latest_data', methods=['GET'])
def get_latest_data():
    try:
        # Retrieve the latest document in the collection
        data = collection.find_one(sort=[('_id', -1)])  # Sorting by _id to get the latest document
        if data:
            if '_id' in data:
                data['_id'] = str(data['_id'])  # Convert ObjectId to string

            print(data)
            return jsonify(data), 200
        else:
            return jsonify({"message": "No data found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
