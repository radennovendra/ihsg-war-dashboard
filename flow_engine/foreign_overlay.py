from flow_engine.foreign_cache_guard import get_foreign_data
from flow_engine.foreign_accel import compute_acceleration
from flow_engine.foreign_sector import sector_rotation

def apply_foreign_overlay(results):

    df = get_foreign_data()   # ⬅️ FAIL-SAFE
    if "Ticker" not in df.columns:
        raise Exception("Foreign data missing Ticker column")
    accel = compute_acceleration()
    sector_flow = sector_rotation(df)

    top_sector = sector_flow.index[0]

    for sym, res in results:

        res["foreign_status"] = accel.get("status")
        res["foreign_sector"] = top_sector

        if res.get("sector") == top_sector:
            res["score"] += 10
            res["foreign_bias"] = "SECTOR_ROTATION"

        if accel["status"] == "STRONG_ACCELERATION":
            res["score"] += 5
        elif accel["status"] == "REVERSAL":
            res["score"] *= 0.8

    return results, accel, top_sector
