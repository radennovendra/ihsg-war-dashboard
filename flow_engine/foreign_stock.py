import pandas as pd
import os

CACHE = "data/foreign_cache/foreign_today.csv"


def load_foreign():
    if not os.path.exists(CACHE):
        print("⚠️ foreign_today.csv not found")
        return pd.DataFrame()

    df = pd.read_csv(CACHE)

    # ==== NORMALIZE COLUMN ====
    rename_map = {
        "StockCode": "Ticker",
        "stockCode": "Ticker",
        "Kode": "Ticker",
    }
    df = df.rename(columns=rename_map)

    # ==== NET FOREIGN ====
    if "ForeignNet" not in df.columns:
        if "ForeignBuy" in df.columns and "ForeignSell" in df.columns:
            df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]
        else:
            print("⚠️ No ForeignNet data")
            return pd.DataFrame()

    if "Ticker" not in df.columns:
        print("⚠️ No Ticker column")
        return pd.DataFrame()

    # ==== CRITICAL FIX ====
    # DO NOT ADD .JK
    df["Ticker"] = df["Ticker"].astype(str).str.upper().str.strip()

    return df


def stock_foreign_map():
    df = load_foreign()

    if df.empty:
        return {}

    fmap = dict(zip(df["Ticker"], df["ForeignNet"]))

    print(f"📦 Foreign map ready: {len(fmap)} stocks")

    return fmap


def classify(net):
    """
    klasifikasi per saham
    """
    if net > 100_000_000_000:
        return "MEGA_ACCUM"
    if net > 30_000_000_000:
        return "STRONG_ACCUM"
    if net > 0:
        return "ACCUM"
    if net < -100_000_000_000:
        return "MEGA_DISTRIB"
    if net < -30_000_000_000:
        return "STRONG_DISTRIB"
    if net < 0:
        return "DISTRIB"
    return "NEUTRAL"