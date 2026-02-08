import requests
import pandas as pd
import time

IDX_API = "https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.idx.co.id/",
}


def fetch_idx_summary():

    for i in range(3):
        try:
            r = requests.get(IDX_API, headers=HEADERS, timeout=20)
            r.raise_for_status()

            data = r.json()["data"]
            df = pd.DataFrame(data)

            # ===== PENTING: RENAME KOLOM =====
            df = df.rename(columns={
                "stockCode": "Ticker",
                "foreignBuy": "ForeignBuy",
                "foreignSell": "ForeignSell"
            })

            df["Ticker"] = df["Ticker"].astype(str)
            df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]

            return df

        except Exception as e:
            print(f"⚠️ IDX fetch failed attempt {i+1} ->", e)
            time.sleep(2)

    raise Exception("❌ IDX API blocked")
