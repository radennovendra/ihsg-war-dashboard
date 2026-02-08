import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data/foreign_history"

def store_daily(df):

    os.makedirs(DATA_DIR, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    path = f"{DATA_DIR}/foreign_{today}.csv"
    df.to_csv(path, index=False)

    return path
