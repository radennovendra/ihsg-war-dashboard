import pandas as pd

# ===============================
# INPUT
# ===============================

LIST_FILE = "Daftar Saham  - 20260202.xlsx"
OUTPUT_FILE = "data/idx_sector_map.csv"

# ===============================
# MULTI PUBLIC SOURCES (fallback chain)
# ===============================

PUBLIC_SOURCES = [
    # Source 1 (community IDX-IC map)
    "https://raw.githubusercontent.com/iqbalharith/idx-sector-map/main/idx_sector_map.csv",

    # Source 2 (alt repo)
    "https://raw.githubusercontent.com/rizkysaputra/idx-ic-classification/main/sector_map.csv",

    # Source 3 (backup repo)
    "https://raw.githubusercontent.com/fintech-id/idx-industry-map/main/idx_sector.csv",
]

# ===============================
# FALLBACK HEURISTIC (last resort)
# ===============================

def heuristic_sector(symbol):
    """
    Very rough proxy if sector missing.
    Based on known IDX patterns.
    """
    if symbol.startswith("BB") or symbol in ["BRIS", "BTPS"]:
        return "BANKS"
    if symbol in ["ADRO", "ITMG", "PTBA", "HRUM"]:
        return "ENERGY"
    if symbol in ["TLKM", "EXCL", "ISAT"]:
        return "TELCO"
    if symbol in ["ICBP", "INDF", "UNVR", "MYOR"]:
        return "CONSUMER"
    if symbol in ["ANTM", "MDKA", "INCO"]:
        return "MATERIALS"
    return "OTHER"


# ===============================
# LOAD PUBLIC SOURCE
# ===============================

def try_load_sources():
    for url in PUBLIC_SOURCES:
        try:
            print("🌍 Trying source:", url)
            df = pd.read_csv(url)

            # Normalize columns
            cols = [c.lower() for c in df.columns]

            if "symbol" not in cols:
                continue

            # Guess sector column name
            sector_col = None
            for c in df.columns:
                if "sector" in c.lower():
                    sector_col = c
                    break

            if not sector_col:
                continue

            df = df.rename(columns={sector_col: "Sector"})
            df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()
            df["Sector"] = df["Sector"].astype(str).str.upper().str.strip()

            print("✅ Loaded source successfully:", url)
            return df[["Symbol", "Sector"]]

        except Exception as e:
            print("❌ Failed:", e)

    return None


# ===============================
# MAIN GENERATOR
# ===============================

def generate():
    print("\n🏛️ BULLETPROOF IDX SECTOR MAP GENERATOR")
    print("======================================")

    # Load full IDX stock list
    stocks = pd.read_excel(LIST_FILE)
    stocks["Symbol"] = stocks["Kode"].astype(str).str.upper().str.strip()

    print("Total stocks:", len(stocks))

    # Load sector sources
    sector_df = try_load_sources()

    if sector_df is None:
        print("⚠️ No public sector dataset available.")
        print("Using heuristic fallback only...")

        stocks["Sector"] = stocks["Symbol"].apply(heuristic_sector)

    else:
        # Merge sector mapping
        merged = stocks.merge(sector_df, on="Symbol", how="left")

        # Fill missing with heuristic proxy
        merged["Sector"] = merged["Sector"].fillna(
            merged["Symbol"].apply(heuristic_sector)
        )

        stocks = merged

    # Output final mapping
    out = stocks[["Symbol", "Sector"]].drop_duplicates()
    out.to_csv(OUTPUT_FILE, index=False)

    # Coverage stats
    missing = (out["Sector"] == "OTHER").sum()
    coverage = 100 * (1 - missing / len(out))

    print("\n✅ Sector map generated!")
    print("Saved to:", OUTPUT_FILE)
    print("Coverage:", f"{coverage:.1f}%")
    print("Missing:", missing)

    print("\nTop sector counts:")
    print(out["Sector"].value_counts().head(10))


if __name__ == "__main__":
    generate()
