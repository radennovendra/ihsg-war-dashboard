import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID


# =========================
# SEND MESSAGE
# =========================
def send(msg):

    if not TELEGRAM_TOKEN:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=10)
    except:
        pass


# =========================
# SEND PHOTO
# =========================
def send_photo(path, caption=None):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

    with open(path, "rb") as img:
        data = {
            "chat_id": CHAT_ID,
            "caption": caption
        }

        files = {
            "photo": img
        }

        r = requests.post(url, data=data, files=files)

    return r.json()


# =========================
# FORMAT MONEY
# =========================
def fmt(net):

    if abs(net) >= 1e12:
        return f"{net/1e12:.2f}T"
    if abs(net) >= 1e9:
        return f"{net/1e9:.1f}B"
    if abs(net) >= 1e6:
        return f"{net/1e6:.1f}M"

    return str(int(net))


def send_file(path):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendDocument"

    with open(path, "rb") as f:
        files = {"document": f}

        data = {
            "chat_id": CHAT_ID
        }

        requests.post(url, files=files, data=data)