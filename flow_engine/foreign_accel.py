import pandas as pd
import glob
import os

HISTORY_DIR = "data/foreign_history"


# =========================
# LOAD HISTORY FILES
# =========================
def load_history(days=5):

    files = sorted(glob.glob(f"{HISTORY_DIR}/foreign_*.csv"))

    if not files:
        return []

    files = files[-days:]

    totals = []

    for f in files:
        try:
            df = pd.read_csv(f)

            if "ForeignNet" not in df.columns:
                continue

            total = float(df["ForeignNet"].sum())
            totals.append(total)

        except:
            continue

    return totals


# =========================
# MAIN ACCEL ENGINE
# =========================
def compute_acceleration():

    totals = load_history(5)

    if len(totals) < 2:
        return {
            "status": "INSUFFICIENT_DATA",
            "net_today": 0,
            "delta": 0,
            "accel": 0
        }

    today = totals[-1]
    yday = totals[-2]

    delta = today - yday

    # kalau belum ada 3 hari data
    if len(totals) < 3:
        accel = delta
    else:
        prev = totals[-3]
        accel = delta - (yday - prev)

    # =========================
    # THRESHOLD REALISTIS IDX
    # =========================
    STRONG = 100_000_000_000   # 100B
    MED = 30_000_000_000       # 30B

    if accel > STRONG:
        status = "STRONG_INFLOW_ACCEL"
    elif accel > MED:
        status = "INFLOW_ACCEL"
    elif accel < -STRONG:
        status = "STRONG_OUTFLOW_ACCEL"
    elif accel < -MED:
        status = "OUTFLOW_ACCEL"
    else:
        status = "NEUTRAL"

    return {
        "net_today": today,
        "delta": delta,
        "accel": accel,
        "status": status
    }
