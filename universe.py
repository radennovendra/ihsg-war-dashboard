import pandas as pd


INPUT_FILE = "Daftar Saham  - 20260202.xlsx"
OUTPUT_FILE = "data/universe.csv"


def update_universe():
    print("📌 Loading IDX stock list from Excel:", INPUT_FILE)

    df = pd.read_excel(INPUT_FILE)

    # Column must contain "Kode"
    if "Kode" not in df.columns:
        raise Exception("❌ Column 'Kode' not found in Excel file")

    # Convert to Yahoo format
    tickers = df["Kode"].astype(str).str.upper().str.strip() + ".JK"

    # Save universe
    tickers.to_csv(OUTPUT_FILE, index=False, header=False)

    print("✅ Universe generated successfully!")
    print("Total stocks:", len(tickers))
    print("Saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    update_universe()
