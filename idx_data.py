import pandas as pd

def load_idx_official(file_path):
    """
    Load IDX official daily trading file.
    Must contain columns:
    Symbol, Close, Volume, Value
    """
    df = pd.read_csv(file_path)

    df["Symbol"] = df["Symbol"].str.upper().str.strip()
    df = df.set_index("Symbol")

    return df
