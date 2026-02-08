import pandas as pd

INPUT_FILE = "idx_ic.xlsx"
OUTPUT_FILE = "data/idx_sector_map.csv"

def generate():
    print("📌 Loading IDX-IC file:", INPUT_FILE)

    df = pd.read_excel(INPUT_FILE)
    df.columns = [c.strip() for c in df.columns]

    symbol_col, sector_col = None, None

    for c in df.columns:
        if "Kode" in c or "Code" in c:
            symbol_col = c
        if "Sektor" in c or "Sector" in c:
            sector_col = c

    if not symbol_col or not sector_col:
        raise Exception("❌ Could not detect Symbol/Sector columns")

    df["Symbol"] = df[symbol_col].astype(str).str.upper().str.strip()
    df["Sector"] = df[sector_col].astype(str).str.upper().str.strip()

    out = df[["Symbol", "Sector"]].drop_duplicates()
    out.to_csv(OUTPUT_FILE, index=False)

    print("✅ Sector map generated:", len(out), "stocks")
    print("Saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    generate()
