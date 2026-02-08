import yfinance as yf


def market_regime():
    """
    Determine market regime based on IHSG (^JKSE) 5-day return.
    Always returns scalar result.
    """

    df = yf.download("^JKSE", period="1mo", interval="1d", progress=False)

    if df.empty or len(df) < 6:
        return "NEUTRAL"

    # Ensure scalar float
    close_today = float(df["Close"].iloc[-1])
    close_5d = float(df["Close"].iloc[-6])

    ret5 = (close_today / close_5d) - 1

    if ret5 < -0.03:
        return "RISK-OFF"
    elif ret5 > 0.02:
        return "RISK-ON"
    else:
        return "NEUTRAL"
