import pandas as pd
import os

SECTOR_FILE = "data/idx_sector_map.csv"

def load_sector_map():
    if not os.path.exists(SECTOR_FILE):
        raise Exception("❌ Sector map missing. Run generate_sector_map.py first.")

    df = pd.read_csv(SECTOR_FILE)
    df["Symbol"] = df["Symbol"].str.upper().str.strip()
    df["Sector"] = df["Sector"].str.upper().str.strip()

    return dict(zip(df["Symbol"], df["Sector"]))

SECTOR_MAP = None

def get_sector(symbol):
    global SECTOR_MAP
    if SECTOR_MAP is None:
        SECTOR_MAP = load_sector_map()

    sym = symbol.replace(".JK", "").upper()
    return SECTOR_MAP.get(sym, "OTHER")
