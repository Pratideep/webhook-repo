from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from bson.json_util import dumps

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["webhook_db"]   # database name
collection = db["events"]   # collection name

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/webhook", methods=["POST"])
def github_webhook():
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event")

    data = {
        "author": "",
        "action": "",
        "from_branch": "",
        "to_branch": "",
        "timestamp": datetime.utcnow()
    }

    if event_type == "push":
        data["author"] = payload["pusher"]["name"]
        data["action"] = "push"
        data["to_branch"] = payload["ref"].split("/")[-1]

    elif event_type == "pull_request":
        pr = payload["pull_request"]
        action = payload["action"]

        if action == "opened":
            data["author"] = pr["user"]["login"]
            data["action"] = "pull_request"
            data["from_branch"] = pr["head"]["ref"]
            data["to_branch"] = pr["base"]["ref"]

        elif action == "closed" and pr["merged"]:
            data["author"] = pr["merged_by"]["login"] if pr["merged_by"] else pr["user"]["login"]
            data["action"] = "merge"
            data["from_branch"] = pr["head"]["ref"]
            data["to_branch"] = pr["base"]["ref"]

        else:
            return jsonify({"msg": "Pull request event ignored"}), 200


    elif event_type == "pull_request" and payload["pull_request"]["merged"]:
        # Optional: handle merge
        data["author"] = payload["pull_request"]["merged_by"]["login"]
        data["action"] = "merge"
        data["from_branch"] = payload["pull_request"]["head"]["ref"]
        data["to_branch"] = payload["pull_request"]["base"]["ref"]

    else:
        return jsonify({"msg": "Event not handled"}), 200

    collection.insert_one(data)
    return jsonify({"msg": "Event stored"}), 200

@app.route("/get-updates", methods=["GET"])
def get_updates():
    docs = collection.find().sort("timestamp", -1).limit(10)
    events = []
    for doc in docs:
        event = {
            "author": doc["author"],
            "action": doc["action"],
            "from_branch": doc["from_branch"],
            "to_branch": doc["to_branch"],
            "timestamp": doc["timestamp"].strftime("%d %B %Y - %I:%M %p UTC")
        }
        events.append(event)
    return dumps(events)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)), debug=True)
