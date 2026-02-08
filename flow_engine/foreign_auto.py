import os
import requests
import pandas as pd
from datetime import datetime

CACHE_DIR = "data/foreign_cache"
HIST_DIR = "data/foreign_history"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(HIST_DIR, exist_ok=True)

URL = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0"

# =========================
# FETCH IDX
# =========================
def fetch_idx():

    ts = str(int(datetime.now().timestamp()*1000))

    url = f"https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&_={ts}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.idx.co.id/",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest"
    }

    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    data = r.json()["data"]
    df = pd.DataFrame(data)

    df["Ticker"] = df["StockCode"]
    df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]

    print("🌍 IDX rows:", len(df))
    print("🌍 TOTAL FOREIGN:", df["ForeignNet"].sum())

    return df[["Ticker","ForeignNet"]]

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

        if abs(new_total - last_total) < 1:
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
        save_history_if_changed()

    print("✅ Done\n")

if __name__ == "__main__":
    main()