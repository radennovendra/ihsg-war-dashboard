import pandas as pd
import os

OUTPUT_FILE = "data/fundamentals.csv"

# Public dataset proxy (example open source IDX fundamentals)
DATA_URL = "https://raw.githubusercontent.com/datasets-id/idx-fundamentals/main/fundamentals.csv"


def build():
    print("\n🏛️ Downloading Public Fundamental Dataset...")
    print("==========================================")

    try:
        df = pd.read_csv(DATA_URL)
    except Exception as e:
        print("❌ Failed to download dataset:", e)
        return

    # Standardize column names
    df.columns = [c.lower().strip() for c in df.columns]

    # Expected columns mapping
    rename_map = {
        "ticker": "symbol",
        "pbv": "pbv",
        "per": "per",
        "roe": "roe",
        "dividend_yield": "div_yield",
        "eps_growth": "eps_growth",
    }

    df = df.rename(columns=rename_map)

    # Keep only needed columns
    keep = ["symbol", "pbv", "per", "roe", "div_yield", "eps_growth"]
    df = df[[c for c in keep if c in df.columns]]

    # Clean symbols
    df["symbol"] = df["symbol"].str.upper().str.strip()

    # Save fundamentals
    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("✅ Fundamentals dataset ready!")
    print("Saved to:", OUTPUT_FILE)
    print("Total rows:", len(df))
    print(df.head(10))


if __name__ == "__main__":
    build()
