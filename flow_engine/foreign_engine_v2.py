import pandas as pd
import glob
import os

HIST_PATH = "data/foreign_history"


# ==========================
# LOAD HISTORY
# ==========================
def load_history(days=5):

    files = sorted(glob.glob(f"{HIST_PATH}/foreign_*.csv"))[-days:]
    if not files:
        return None

    dfs = []
    for f in files:
        df = pd.read_csv(f)
        dfs.append(df)

    return dfs


# ==========================
# BUILD STOCK MATRIX
# ==========================
def build_matrix(dfs):

    merged = {}

    for i, df in enumerate(dfs):
        for _, row in df.iterrows():
            t = row["Ticker"]
            merged.setdefault(t, []).append(row["ForeignNet"])

    return merged


# ==========================
# PER STOCK ANALYSIS
# ==========================
def analyze_stock_flow(matrix):

    out = {}

    for t, arr in matrix.items():

        if len(arr) < 2:
            continue

        today = arr[-1]
        yday = arr[-2]

        delta = today - yday

        if len(arr) >= 3:
            prev = arr[-3]
            accel = delta - (yday - prev)
        else:
            accel = 0

        momentum = sum(arr)

        out[t] = {
            "net": today,
            "delta": delta,
            "accel": accel,
            "momentum": momentum
        }

    return out


# ==========================
# RANKING ENGINE
# ==========================
def rank_foreign(flow):

    ranked = sorted(
        flow.items(),
        key=lambda x: x[1]["momentum"],
        reverse=True
    )

    return ranked


# ==========================
# CLASSIFICATION
# ==========================
def classify_flow(d):

    net = d["net"]
    accel = d["accel"]

    if net > 100_000_000_000 and accel > 0:
        return "SMART MONEY ACCUM"

    if net > 0 and accel > 0:
        return "ACCUM"

    if net < -100_000_000_000:
        return "DISTRIBUTION"

    return "NEUTRAL"


# ==========================
# MAIN ENGINE
# ==========================
def run_foreign_engine():

    dfs = load_history(5)
    if dfs is None or len(dfs) < 2:
        return None, "INSUFFICIENT_DATA"

    matrix = build_matrix(dfs)
    flow = analyze_stock_flow(matrix)
    ranked = rank_foreign(flow)

    return ranked, "READY"
