import os
import json
from datetime import datetime

FILE = "runtime/twitter_history.json"

def load():

    if not os.path.exists(FILE):
        return {}

    with open(FILE, "r") as f:
        return json.load(f)


def save(data):

    os.makedirs("runtime", exist_ok=True)

    with open(FILE, "w") as f:
        json.dump(data, f)


def allow(symbol):

    data = load()

    today = datetime.now().strftime("%Y-%m-%d")

    if symbol in data and data[symbol] == today:
        return False

    data[symbol] = today
    save(data)

    return True