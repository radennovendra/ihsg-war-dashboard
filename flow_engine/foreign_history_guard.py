import os
import pandas as pd
from datetime import datetime

CACHE = "data/foreign_cache/foreign_today.csv"
HISTORY = "data/foreign_history"


def save_history_if_changed():

    if not os.path.exists(CACHE):
        print("No cache")
        return

    today = datetime.now().strftime("%Y-%m-%d")
    new_file = f"{HISTORY}/foreign_{today}.csv"

    new_df = pd.read_csv(CACHE)
    new_total = new_df["ForeignNet"].sum()

    files = sorted(os.listdir(HISTORY))
    if files:
        last_file = files[-1]
        last_df = pd.read_csv(f"{HISTORY}/{last_file}")
        last_total = last_df["ForeignNet"].sum()

        if abs(new_total - last_total) < 1e-6:
            print("⚠️ Foreign unchanged → skip history save")
            return

    new_df.to_csv(new_file, index=False)
    print("✅ Saved new foreign history:", new_file)