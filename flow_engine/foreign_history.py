import os
import shutil
import pandas as pd

TODAY = "data/foreign_cache/foreign_today.csv"
YDAY = "data/foreign_cache/foreign_yesterday.csv"


def rotate_history():
    """
    Simpan foreign_today jadi foreign_yesterday
    sebelum download data baru
    """

    if not os.path.exists(TODAY):
        print("⚠️ No foreign_today.csv yet")
        return

    try:
        shutil.copy(TODAY, YDAY)
        print("📦 Foreign history rotated (today → yesterday)")
    except Exception as e:
        print("❌ Failed rotate:", e)


def ensure_cache_structure():
    os.makedirs("data/foreign_cache", exist_ok=True)
