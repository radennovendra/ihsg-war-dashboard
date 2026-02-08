import os
import glob
import pandas as pd
from datetime import datetime
from flow_engine.idx_downloader import fetch_idx_summary

CACHE_DIR = "data/foreign_cache"
TODAY_FILE = f"{CACHE_DIR}/foreign_today.csv"


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize column names from IDX/Excel into:
    Ticker, ForeignBuy, ForeignSell, ForeignNet
    """
    rename_map = {
        "stockCode": "Ticker",
        "StockCode": "Ticker",
        "Stock Code": "Ticker",
        "Kode": "Ticker",
        "foreignBuy": "ForeignBuy",
        "Foreign Buy": "ForeignBuy",
        "foreignSell": "ForeignSell",
        "Foreign Sell": "ForeignSell",
    }

    df = df.rename(columns=rename_map)

    if "Ticker" not in df.columns:
        raise Exception("Foreign data missing Ticker column")

    df["Ticker"] = df["Ticker"].astype(str)

    if "ForeignNet" not in df.columns and "ForeignBuy" in df.columns:
        df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]

    return df


def _load_latest_history():
    files = sorted(glob.glob(f"{CACHE_DIR}/foreign_*.csv"))
    if not files:
        raise Exception("❌ No foreign cache available")
    df = pd.read_csv(files[-1])
    return _normalize(df)


def get_foreign_data() -> pd.DataFrame:
    """
    Main entry used by scanner.
    Fail-safe:
    1. Use foreign_today.csv if exists
    2. Else fetch from IDX
    3. Else fallback to last history
    """

    os.makedirs(CACHE_DIR, exist_ok=True)

    # ===== 1️⃣ USE TODAY CACHE =====
    if os.path.exists(TODAY_FILE):
        print("📦 Using cached foreign_today.csv")
        df = pd.read_csv(TODAY_FILE)
        return _normalize(df)

    # ===== 2️⃣ TRY FETCH IDX =====
    try:
        print("🌍 Fetching foreign data from IDX...")
        df = fetch_idx_summary()
        df = _normalize(df)

        today = datetime.now().strftime("%Y-%m-%d")
        dated_file = f"{CACHE_DIR}/foreign_{today}.csv"

        df.to_csv(dated_file, index=False)
        df.to_csv(TODAY_FILE, index=False)

        print("✅ Foreign cached")
        return df

    except Exception as e:
        print("⚠️ IDX unavailable → fallback history", e)
        return _load_latest_history()
