import yfinance as yf
import numpy as np


def backtest(symbol):
    """
    Bulletproof backtest:
    Returns scalar floats only (no warnings, no ambiguity).
    """

    df = yf.download(
        symbol,
        period="1y",
        interval="1d",
        progress=False,
        threads=False
    )

    if df is None or df.empty or len(df) < 30:
        return 0.0, 0.0

    close = df["Close"]

    # Forward returns
    ret5 = (close.shift(-5) / close) - 1
    ret20 = (close.shift(-20) / close) - 1

    ret5 = ret5.dropna()
    ret20 = ret20.dropna()

    if len(ret5) == 0 or len(ret20) == 0:
        return 0.0, 0.0

    # Winrates (scalar safe)
    win5 = float(((ret5 > 0).mean()).item())
    win20 = float(((ret20 > 0).mean()).item())

    return win5, win20

import numpy as np

def hedge_expectancy(df, horizon=20):
    """
    Hedge fund expectancy model.
    Returns:
    winrate, avg_win, avg_loss, expectancy, profit_factor
    """

    close = df["Close"]

    if len(close) < horizon + 30:
        return None

    # Forward returns
    fwd = close.shift(-horizon) / close - 1
    fwd = fwd.dropna()

    wins = fwd[fwd > 0]
    losses = fwd[fwd <= 0]

    winrate = float(len(wins) / len(fwd))

    avg_win = float(wins.mean()) if len(wins) > 0 else 0
    avg_loss = float(abs(losses.mean())) if len(losses) > 0 else 0

    expectancy = (winrate * avg_win) - ((1 - winrate) * avg_loss)

    total_gain = float(wins.sum()) if len(wins) > 0 else 0
    total_loss = float(abs(losses.sum())) if len(losses) > 0 else 1e-9

    profit_factor = total_gain / total_loss

    return winrate, avg_win, avg_loss, expectancy, profit_factor
