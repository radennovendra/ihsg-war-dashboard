import pandas as pd
import os

CACHE = "data/foreign_cache/foreign_today.csv"


def load_foreign():

    if not os.path.exists(CACHE):
        print("⚠️ foreign_today.csv not found")
        return pd.DataFrame()

    df = pd.read_csv(CACHE)

    # normalize kolom
    rename = {
        "StockCode": "Ticker",
        "stockCode": "Ticker",
        "Kode": "Ticker",
    }

    df = df.rename(columns=rename)

    if "ForeignNet" not in df.columns:
        if "ForeignBuy" in df.columns and "ForeignSell" in df.columns:
            df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]

    if "Ticker" not in df.columns:
        print("⚠️ Ticker column missing")
        return pd.DataFrame()

    df["Ticker"] = df["Ticker"].astype(str).str.upper() + ".JK"

    return df[["Ticker", "ForeignNet"]]


def stock_foreign_map():
    df = load_foreign()

    if df.empty:
        return {}

    return dict(zip(df["Ticker"], df["ForeignNet"]))


def classify(net):

    if net > 100_000_000_000:
        return "HEAVY_ACCUM"
    if net > 20_000_000_000:
        return "ACCUM"
    if net < -100_000_000_000:
        return "HEAVY_DISTRIB"
    if net < -20_000_000_000:
        return "DISTRIB"
    return "NEUTRAL"