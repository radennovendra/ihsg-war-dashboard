import pandas as pd
import yfinance as yf

INPUT_FILE = "data/universe.csv"
OUTPUT_FILE = "data/universe_institutional.csv"

MIN_AVG_VALUE = 50_000_000_000   # Rp 50B/day liquidity
MAX_STOCKS = 200                 # Top 200 institutional names


def avg_traded_value(symbol):
    """
    Calculate avg traded value over last 20 trading days.
    """
    try:
        df = yf.download(symbol, period="1mo", interval="1d", progress=False)

        if df.empty or len(df) < 10:
            return 0

        value = (df["Close"] * df["Volume"]).mean()
        return float(value)

    except:
        return 0


def build():
    print("\n🏛️ Building Institutional Universe (Top Liquidity 200)")
    print("=====================================================")

    tickers = pd.read_csv(INPUT_FILE, header=None)[0].tolist()

    scores = []
    for i, sym in enumerate(tickers):

        # Skip invalid tickers
        if sym.startswith("$"):
            continue

        if i % 50 == 0:
            print(f"Checking {i}/{len(tickers)} stocks...")

        v = avg_traded_value(sym)

        if v > 0:
            scores.append((sym, v))

    # Sort by liquidity
    scores.sort(key=lambda x: x[1], reverse=True)

    # Filter top liquid names
    elite = [s for s, v in scores if v >= MIN_AVG_VALUE][:MAX_STOCKS]

    pd.DataFrame(elite).to_csv(OUTPUT_FILE, index=False, header=False)

    print("\n✅ Institutional Universe Ready!")
    print("Total elite stocks:", len(elite))
    print("Saved to:", OUTPUT_FILE)
    print("Example:", elite[:10])


if __name__ == "__main__":
    build()
