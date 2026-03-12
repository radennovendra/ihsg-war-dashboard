import time
from datetime import datetime

from scanner import run
from utils.entry_engine import check_entry_engine
from utils.yahoo_pro import download_price
from alerts.telegram_alert import send_telegram

alert_memory = {}
ALERT_COOLDOWN = 1800
ENTRY_INTERVAL = 600  # 10 menit


# =========================
# MARKET CLOCK
# =========================

def market_open():

    now = datetime.now()

    t = now.hour * 60 + now.minute

    session1 = 9*60 <= t <= 11*60+30
    session2 = 13*60+30 <= t <= 15*60

    return session1 or session2

# =========================
# COOLDOWN
# =========================

def cooldown_ok(sym):

    now = time.time()

    last = alert_memory.get(sym)

    if last is None:
        return True

    if now - last > ALERT_COOLDOWN:
        return True

    return False


# =========================
# ENTRY MONITOR
# =========================

def entry_monitor(setups):

    print("🔎 Checking entry alerts")

    for r in setups:

        sym = r["symbol"]

        try:

            # ====================
            # RETRY DOWNLOAD PRICE
            # ====================

            df = None

            for _ in range(3):

                df = download_price(sym)

                if df is not None and not df.empty:
                    break

                time.sleep(1)

            if df is None or df.empty:
                continue

            # ====================
            # ENTRY CHECK
            # ====================

            alert = check_entry_engine(sym, df, r)

            if alert["alert"]:

                msg = f"""
🚨 ENTRY ALERT

Ticker : {sym}
Price  : {alert['price']}

Signals :
{", ".join(alert['signals'])}

Entry Zone : {r['entry_low']} - {r['entry_high']}
Stop Loss  : {r['stoploss']}
Take Profit: {r['tp2']}
"""

                print(msg)

                send_telegram(msg)

        except Exception as e:

            print("Entry alert error:", sym, e)


# =========================
# MASTER CONTROLLER
# =========================

def run():

    print("🚀 IHSG WAR Scanner Started")

    # ---------------------
    # RUN SCANNER ONCE
    # ---------------------

    print("📊 Running scanner...")

    setups = run()

    print(f"📌 Watchlist: {len(setups)} saham")


    # ---------------------
    # ENTRY LOOP
    # ---------------------

    while True:

        if market_open():

            entry_monitor(setups)

            time.sleep(ENTRY_INTERVAL)

        else:

            print("⏸ Market closed")

            time.sleep(60)


if __name__ == "__main__":

    run()