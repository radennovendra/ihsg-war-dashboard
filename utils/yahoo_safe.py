import yfinance as yf
import time
import pandas as pd


# =====================================
# SAFE YAHOO DOWNLOAD (ANTI CRASH)
# =====================================
def safe_download(symbol, period="3mo", retries=3, pause=0.8):

    for attempt in range(retries):

        try:
            df = yf.download(
                symbol,
                period=period,
                progress=False,
                threads=False
            )

            # =========================
            # VALIDATION
            # =========================
            if df is None:
                raise Exception("None dataframe")

            if isinstance(df, pd.DataFrame) and df.empty:
                raise Exception("Empty dataframe")

            if len(df) < 30:
                raise Exception("Too short")

            # Fix MultiIndex columns (Yahoo bug)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            return df

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(pause)
            else:
                print(f"❌ Yahoo failed {symbol}")
                return None

    return None