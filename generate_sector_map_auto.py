import pandas as pd
import yfinance as yf
import time
import os

UNIVERSE_FILE = "data/universe.csv"
OUTPUT_FILE = "data/sector_map.csv"


def get_sector(ticker):
    try:
        t = yf.Ticker(ticker + ".JK")
        info = t.info

        sector = info.get("sector")
        if sector:
            return sector

    except Exception:
        pass

    return "Unknown"


def run():

    if not os.path.exists(UNIVERSE_FILE):
        raise Exception("❌ universe.csv not found in data/")

    df = pd.read_csv(UNIVERSE_FILE, header=None)
    tickers = df[0].tolist()

    rows = []

    print("🏭 Building sector map...\n")

    for i, t in enumerate(tickers):
        print(f"{i+1}/{len(tickers)} → {t}")

        sector = get_sector(t)

        rows.append({
            "Ticker": t + ".JK",
            "Sector": sector
        })

        time.sleep(0.3)  # anti rate-limit

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_FILE, index=False)

    print("\n✅ sector_map.csv created at:", OUTPUT_FILE)


if __name__ == "__main__":
    run()
