import pandas as pd
import os

FUND_FILE = "data/fundamentals.csv"


def load_fundamentals():
    """
    Load valuation dataset if exists.
    Columns expected:
    symbol, pbv, per, roe, div_yield, eps_growth
    """
    if not os.path.exists(FUND_FILE):
        return None

    df = pd.read_csv(FUND_FILE)
    df["symbol"] = df["symbol"].str.upper().str.strip()
    return df.set_index("symbol")


def get_fundamental(symbol, fund_db):
    """
    Return dict of fundamentals or None
    """
    if fund_db is None:
        return None

    sym = symbol.replace(".JK", "")
    if sym not in fund_db.index:
        return None

    row = fund_db.loc[sym]
    return row.to_dict()
