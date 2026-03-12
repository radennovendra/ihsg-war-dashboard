def entry_score(df, r):

    signals = []

    price = df["Close"].iloc[-1]

    entry_low = float(r["entry_low"])
    entry_high = float(r["entry_high"])

    # ======================
    # EMA TREND
    # ======================

    if df["EMA9"].iloc[-1] > df["EMA9"].iloc[-2]:
        signals.append("EMA_UP")

    # ======================
    # ENTRY ZONE
    # ======================

    if entry_low <= price <= entry_high:
        signals.append("ENTRY_ZONE")

    # ======================
    # VOLUME EXPANSION
    # ======================

    vol = df["Volume"].iloc[-1]
    avg = df["Volume"].rolling(20).mean().iloc[-1]

    if vol > avg * 1.3:
        signals.append("VOLUME_EXPANSION")

    # ======================
    # LIQUIDITY SWEEP
    # ======================

    if df["Low"].iloc[-1] < df["Low"].iloc[-2] and price > df["Low"].iloc[-2]:
        signals.append("LIQUIDITY_SWEEP")

    # ======================
    # PRE BREAKOUT
    # ======================

    high20 = df["High"].rolling(20).max().iloc[-1]

    if price > high20 * 0.97:
        signals.append("PRE_BREAKOUT")

    score = len(signals)

    return score, signals