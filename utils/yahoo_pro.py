import yfinance as yf
import pandas as pd
import time
import random
import os

CACHE_DIR = "data/price_cache"
os.makedirs(CACHE_DIR, exist_ok=True)


# =========================================
# DOWNLOAD WITH CACHE + RETRY + FALLBACK
# =========================================
def download_price(symbol, period="3mo", retries=3):

    cache_file = f"{CACHE_DIR}/{symbol.replace('.JK','')}.csv"

    for attempt in range(retries):

        try:
            df = yf.download(
                symbol,
                period=period,
                progress=False,
                threads=False
            )

            if df is None or df.empty or len(df) < 30:
                raise Exception("Invalid data")

            # Fix Yahoo MultiIndex bug
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # SAVE CACHE
            df.to_csv(cache_file)

            return df

        except Exception as e:
            time.sleep(0.7 + random.random())

    # =========================
    # FALLBACK TO CACHE
    # =========================
    if os.path.exists(cache_file):
        try:
            df = pd.read_csv(cache_file, index_col=0)
            return df
        except:
            pass

    print(f"❌ TOTAL FAIL {symbol}")
    return None
