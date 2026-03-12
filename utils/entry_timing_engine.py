def entry_timing(df, entry_low, entry_high):

    signals = []

    price = df["Close"].iloc[-1]

    ema9 = df["Close"].ewm(span=9).mean().iloc[-1]
    ma20 = df["Close"].rolling(20).mean().iloc[-1]

    typical = (df["High"] + df["Low"] + df["Close"]) / 3
    vwap = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()

    vol = df["Volume"].iloc[-1]
    avgvol = df["Volume"].rolling(20).mean().iloc[-1]

    # TREND
    if ema9 > ma20:
        signals.append("TREND")

    # ENTRY MIDPOINT
    mid = (entry_low + entry_high) / 2
    if abs(price - mid) / mid < 0.03:
        signals.append("ENTRY_ZONE")

    # VOLUME
    if vol > avgvol * 1.5:
        signals.append("VOLUME")

    # VWAP RECLAIM
    if df["Close"].iloc[-1] > vwap.iloc[-1] and df["Close"].iloc[-2] <= vwap.iloc[-2]:
        signals.append("VWAP_RECLAIM")

    # BREAKOUT
    if df["Close"].iloc[-1] > df["High"].iloc[-2]:
        signals.append("BREAKOUT")

    score = len(signals)

    return score, signals