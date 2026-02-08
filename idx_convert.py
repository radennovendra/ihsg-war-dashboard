import pandas as pd

def convert_idx_file(raw_file, output="data/idx_official/prices_today.csv"):
    """
    Convert IDX raw trading summary into scanner format.
    """

    df = pd.read_excel(raw_file)

    # Rename columns depending on IDX format
    df = df.rename(columns={
        "Kode": "Symbol",
        "Penutupan": "Close",
        "Volume": "Volume",
        "Nilai": "Value"
    })

    df = df[["Symbol", "Close", "Volume", "Value"]]

    df.to_csv(output, index=False)

    print("✅ Converted IDX official file saved:", output)


if __name__ == "__main__":
    convert_idx_file("data/raw_idx.xlsx")
