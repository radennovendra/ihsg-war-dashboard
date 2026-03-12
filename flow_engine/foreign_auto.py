import os
import requests
import pandas as pd
import time
import random
from datetime import datetime

CACHE_DIR = "data/foreign_cache"
HIST_DIR = "data/foreign_history"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(HIST_DIR, exist_ok=True)

IDX_ENDPOINT = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary"

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5)",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
]


def fetch_idx():

    session = requests.Session()

    time.sleep(random.uniform(1,3))

    for attempt in range(5):

        try:

            ts = str(int(datetime.now().timestamp()*1000))

            url = f"{IDX_ENDPOINT}?length=9999&start=0&_={ts}"

            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Referer": "https://www.idx.co.id/",
                "Accept": "application/json, text/plain, */*",
                "X-Requested-With": "XMLHttpRequest",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "Connection": "keep-alive"
            }

            r = session.get(url, headers=headers, timeout=20)

            r.raise_for_status()

            data = r.json().get("data")

            if not data:
                raise Exception("Empty IDX data")

            df = pd.DataFrame(data)

            df.columns = [c.lower() for c in df.columns]

            df = df.rename(columns={
                "stockcode": "Ticker",
                "foreignbuy": "ForeignBuy",
                "foreignsell": "ForeignSell"
            })
            
            required = ["Ticker", "ForeignBuy", "ForeignSell"]

            for c in required:
                if c not in df.columns:
                    raise Exception(f"IDX column missing: {c}")
            
            df = df.dropna(subset=["Ticker"])

            df["Ticker"] = df["Ticker"].astype(str)

            df["ForeignBuy"] = pd.to_numeric(df["ForeignBuy"], errors="coerce").fillna(0)
            df["ForeignSell"] = pd.to_numeric(df["ForeignSell"], errors="coerce").fillna(0)

            df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]

            df = df[["Ticker","ForeignNet"]]

            print("🌍 IDX rows:", len(df))
            print("🌍 TOTAL FOREIGN:", int(df["ForeignNet"].sum()))

            return df

        except Exception as e:

            print(f"⚠️ IDX attempt {attempt+1} failed -> {e}")

            # exponential backoff
            sleep_time = random.uniform(2,5) * (attempt+1)

            time.sleep(sleep_time)

    raise Exception("❌ IDX API blocked after retries")

# =========================
# SAVE TODAY
# =========================
def save_today(df):

    today = datetime.now().strftime("%Y-%m-%d")

    cache_path = f"{CACHE_DIR}/foreign_today.csv"
    hist_path = f"{HIST_DIR}/foreign_{today}.csv"

    df.to_csv(cache_path, index=False)
    df.to_csv(hist_path, index=False)

    print("📦 Foreign saved:", today)

# =========================
# AUTO FETCH
# =========================
def auto_fetch():

    try:
        print("📥 Fetching IDX foreign flow...")
        df = fetch_idx()
        save_today(df)
        return df

    except Exception as e:
        print("⚠️ IDX blocked → using cache")

        cache = f"{CACHE_DIR}/foreign_today.csv"
        if os.path.exists(cache):
            return pd.read_csv(cache)

        print("❌ No foreign data available")
        return None

# =========================
# SAVE HISTORY IF CHANGED
# =========================
def save_history_if_changed():

    cache_path = f"{CACHE_DIR}/foreign_today.csv"
    if not os.path.exists(cache_path):
        print("No foreign_today.csv")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    new_path = f"{HIST_DIR}/foreign_{today}.csv"

    new_df = pd.read_csv(cache_path)
    new_total = new_df["ForeignNet"].sum()

    files = sorted(os.listdir(HIST_DIR))
    if files:
        last = files[-1]
        last_df = pd.read_csv(f"{HIST_DIR}/{last}")
        last_total = last_df["ForeignNet"].sum()

        if abs(new_total - last_total) < 100000000:
            print("⚠️ Foreign not changed → skip history save")
            return

    new_df.to_csv(new_path, index=False)
    print("📚 New foreign history saved:", new_path)

# =========================
# MAIN
# =========================
def main():
    print("\n🌍 FOREIGN AUTO ENGINE")
    df = auto_fetch()

    if df is not None:

        print(df.sort_values("ForeignNet", ascending=False).head(5))

        save_history_if_changed()

    print("✅ Done\n")



if __name__ == "__main__":
    main()