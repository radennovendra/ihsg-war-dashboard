import json, os

STATE_FILE = "sector_state.json"

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    return json.load(open(STATE_FILE))

def save_state(state):
    json.dump(state, open(STATE_FILE, "w"))

def detect_shift(today_leader):
    state = load_state()
    prev = state.get("leader")

    shifted = prev and prev != today_leader

    state["leader"] = today_leader
    save_state(state)

    return shifted, prev
