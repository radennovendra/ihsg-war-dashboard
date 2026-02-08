import pandas as pd

def compute_sector_leaders(results):
    rows = []
    for sym, r in results:
        rows.append({
            "Sector": r["sector"],
            "Ret5": r["ret5"],
            "Ret20": r["ret20"]
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return None

    sector_perf = df.groupby("Sector").mean()
    sector_perf["BlendScore"] = 0.6 * sector_perf["Ret20"] + 0.4 * sector_perf["Ret5"]

    return sector_perf.sort_values("BlendScore", ascending=False)
