import pandas as pd
import os

SECTOR_MAP = "data/sector_map.csv"


def sector_rotation(df):
    """
    Calculate sector foreign flow safely.
    Will NOT crash if sector_map.csv missing.
    """

    # ===== FAIL-SAFE =====
    if not os.path.exists(SECTOR_MAP):
        print("⚠️ sector_map.csv not found → using UNKNOWN sector")
        df["Sector"] = "Unknown"
        return df.groupby("Sector")["ForeignNet"].sum()

    # ===== LOAD MAP =====
    smap = pd.read_csv(SECTOR_MAP)

    # normalize ticker
    smap["Ticker"] = smap["Ticker"].str.replace(".JK", "", regex=False)
    df["Ticker"] = df["Ticker"].astype(str)

    # merge
    df = df.merge(smap, on="Ticker", how="left")
    df["Sector"] = df["Sector"].fillna("Unknown")

    sector_flow = (
        df.groupby("Sector")["ForeignNet"]
        .sum()
        .sort_values(ascending=False)
    )

    return sector_flow
