def accumulation_strength(df):
    """
    Detect broker-style accumulation:
    High volume + flat price + tight candles
    """

    close = df["Close"]
    vol = df["Volume"]

    avg_vol20 = float(vol.rolling(20).mean().iloc[-1].item())

    # Flat return 5 days
    ret5 = float(((close.iloc[-1] / close.iloc[-6]) - 1).item())

    # Tight candle ranges
    ranges = (df["High"] - df["Low"]) / close
    tight = float(ranges.tail(5).mean().item()) < 0.02

    # Volume pressure
    vol_pressure = float(vol.tail(5).mean().item()) > 1.8 * avg_vol20

    if abs(ret5) < 0.03 and tight and vol_pressure:
        return True

    return False
