import requests
import pandas as pd
import time


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.idx.co.id/",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}


def fetch_idx_summary():

    session = requests.Session()

    for i in range(3):

        try:

            url = f"https://www.idx.co.id/primary/TradingSummary/GetStockSummary?length=9999&start=0&_={int(time.time())}"

            r = session.get(url, headers=HEADERS, timeout=20)

            r.raise_for_status()

            data = r.json().get("data")

            if not data:
                raise Exception("IDX returned empty data")

            df = pd.DataFrame(data)

            df = df.rename(columns={
                "stockCode": "Ticker",
                "foreignBuy": "ForeignBuy",
                "foreignSell": "ForeignSell"
            })

            df["Ticker"] = df["Ticker"].astype(str)

            df["ForeignBuy"] = pd.to_numeric(df["ForeignBuy"], errors="coerce")
            df["ForeignSell"] = pd.to_numeric(df["ForeignSell"], errors="coerce")

            df["ForeignNet"] = df["ForeignBuy"] - df["ForeignSell"]

            df = df[["Ticker","ForeignBuy","ForeignSell","ForeignNet"]]

            return df

        except Exception as e:

            print(f"⚠️ IDX fetch failed attempt {i+1} -> {e}")

            time.sleep(2)

    raise Exception("❌ IDX API blocked")