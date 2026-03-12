import os
import time
import pandas as pd
from datetime import datetime

from utils.yahoo_pro import download_price
from telegram_engine import send, send_photo
from utils.chart_generator import generate_chart
from utils.entry_scoring import entry_score


WATCHLIST_FILE = "runtime/watchlist.csv"

CHECK_INTERVAL = 600   # 10 minutes
ALERT_COOLDOWN = 1800  # 30 minutes


def market_open():

    now = datetime.now()
    t = now.hour * 60 + now.minute

    session1 = 9*60 <= t <= 11*60+30
    session2 = 13*60+30 <= t <= 15*60

    return session1 or session2

# ==========================
# ALERT MEMORY
# ==========================

alert_memory = {}


def cooldown_ok(sym):

    now = time.time()

    last = alert_memory.get(sym)

    if last is None:
        return True

    if now - last > ALERT_COOLDOWN:
        return True

    return False


def mark_alert(sym):

    alert_memory[sym] = time.time()


# ==========================
# ENTRY DETECTION
# ==========================

def detect_entry(sym, r):

    df = None
    for _ in range(3):
        df = download_price(sym)
        if df is not None and not df.empty:
            break
        time.sleep(1)

    if df is None or df.empty or len(df) < 30:
        return None

    df = df.tail(30).copy()

    # ========================
    # INDICATORS
    # ========================

    df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()
    df["MA20"] = df["Close"].rolling(20).mean()

    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    df["VWAP"] = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()

    price = df["Close"].iloc[-1]

    entry_low = float(r["entry_low"])
    entry_high = float(r["entry_high"])

    # ========================
    # AVOID CHASING
    # ========================

    if price > entry_high * 1.03:
        return None

    # ========================
    # VOLUME
    # ========================

    vol = df["Volume"].iloc[-1]
    avgvol = df["Volume"].rolling(20).mean().iloc[-1]

    if pd.isna(avgvol) or avgvol == 0:
        avgvol = vol

    confirmations = []

    # ========================
    # TREND
    # ========================

    if df["EMA9"].iloc[-1] > df["MA20"].iloc[-1]:
        confirmations.append("TREND")

    # ========================
    # ENTRY MIDPOINT FILTER
    # ========================

    mid = (entry_low + entry_high) / 2

    if entry_low <= price <= entry_high:
        if abs(price - mid) / mid < 0.03:
            confirmations.append("ENTRY_ZONE")

    # ========================
    # VOLUME SPIKE
    # ========================

    if vol > avgvol * 1.5:
        confirmations.append("VOLUME")

    # ========================
    # EMA RECLAIM
    # ========================

    if (
        df["Close"].iloc[-1] > df["EMA9"].iloc[-1] and
        df["Close"].iloc[-2] <= df["EMA9"].iloc[-2]
    ):
        confirmations.append("EMA_RECLAIM")

    # ========================
    # VWAP RECLAIM
    # ========================

    if (
        df["Close"].iloc[-1] > df["VWAP"].iloc[-1] and
        df["Close"].iloc[-2] <= df["VWAP"].iloc[-2]
    ):
        confirmations.append("VWAP_RECLAIM")

    # ========================
    # MOMENTUM BREAKOUT
    # ========================

    if df["Close"].iloc[-1] > df["High"].iloc[-2]:
        confirmations.append("BREAKOUT")

    # ========================
    # SCORE
    # ========================

    score = len(confirmations)

    if score < 3:
        return None

    confidence = "MEDIUM"

    if score >= 4:
        confidence = "HIGH"

    return {
        "price": price,
        "confirmations": confirmations,
        "score": score,
        "confidence": confidence
    }

# ==========================
# BUILD TELEGRAM MESSAGE
# ==========================

def build_message(sym, r, signal):

    entry = f"{int(r['entry_low'])}-{int(r['entry_high'])}"

    conf = "\n".join([f"• {s}" for s in signal["confirmations"]])

    return f"""
🚨 ENTRY ALERT

{sym}

💰 Price : {signal['price']:.0f}

🎯 Entry : {entry}
🛑 SL    : {int(r['stoploss'])}
🏁 TP    : {int(r['tp2'])}

📊 Confirmations
{conf}

⚡ Entry Score : {signal['score']}/5
Confidence     : {signal['confidence']}

🕒 {datetime.now().strftime("%H:%M")}
"""

# ==========================
# LOAD WATCHLIST
# ==========================

def load_watchlist():

    if not os.path.exists(WATCHLIST_FILE):
        print("Watchlist not found")
        return []

    df = pd.read_csv(WATCHLIST_FILE)

    return df.to_dict("records")


# ==========================
# ENTRY MONITOR LOOP
# ==========================

def run():

    print("\n⚡ ENTRY ALERT ENGINE STARTED")

    while True:

        if not market_open():

            print("Market Closed")
            time.sleep(60)
            continue

        try:

            watchlist = load_watchlist()

            if not watchlist:
                print("No watchlist loaded")
                time.sleep(CHECK_INTERVAL)
                continue

            print("\nChecking entries", datetime.now())

            for r in watchlist:

                sym = r["symbol"]

                try:

                    signal = detect_entry(sym, r)

                    if signal is None:
                        continue

                    if not cooldown_ok(sym):
                        continue

                    msg = build_message(sym, r, signal)

                    send(msg)

                    chart = generate_chart(sym, r)

                    if chart and os.path.exists(chart):
                        send_photo(chart)

                    mark_alert(sym)

                    print("Alert:", sym)

                except Exception as e:

                    print("Entry error", sym, e)

        except Exception as e:

            print("Engine error", e)

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()