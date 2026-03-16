import pandas as pd
import numpy as np

# =========================
# SIGNAL BACKTEST
# BUY → SELL
# =========================

def backtest_signal(df, fee=0.001):

    trades = []
    position = None
    entry = None

    for i in range(len(df)):

        price = df["Close"].iloc[i]

        buy = df["BUY"].iloc[i]
        sell = df["SELL"].iloc[i]

        if pd.notna(buy) and position is None:

            entry = price
            position = True

        elif pd.notna(sell) and position:

            ret = (price - entry) / entry
            ret -= fee * 2

            trades.append(ret)
            position = None

    return trades


# =========================
# TP SL BACKTEST
# =========================

def backtest_tp_sl(df, sl=0.07, tp=0.15):

    trades = []
    position = None
    entry = None

    for i in range(len(df)):

        price = df["Close"].iloc[i]

        if pd.notna(df["BUY"].iloc[i]) and position is None:

            entry = price
            position = True

        if position:

            high = df["High"].iloc[i]
            low = df["Low"].iloc[i]

            if high >= entry * (1 + tp):

                ret = tp - 0.002
                trades.append(ret)
                position = None

            elif low <= entry * (1 - sl):

                ret = -sl - 0.002
                trades.append(ret)
                position = None

    return trades


# =========================
# TRAILING STOP BACKTEST
# =========================

def backtest_trailing(df, trail=0.08):

    trades = []
    position = None
    entry = None
    high_since_entry = None

    for i in range(len(df)):

        price = df["Close"].iloc[i]

        if pd.notna(df["BUY"].iloc[i]) and position is None:

            entry = price
            high_since_entry = price
            position = True

        if position:

            high_since_entry = max(high_since_entry, df["High"].iloc[i])

            stop = high_since_entry * (1 - trail)

            if df["Low"].iloc[i] <= stop:

                ret = (stop - entry) / entry
                ret -= 0.002
                trades.append(ret)

                position = None

    return trades


# =========================
# STATS FUNCTION
# =========================

def calc_stats(trades):

    if len(trades) == 0:
        return None

    trades = np.array(trades)

    wins = trades[trades > 0]
    losses = trades[trades <= 0]

    winrate = len(wins) / len(trades)

    gross_profit = wins.sum()
    gross_loss = abs(losses.sum())

    pf = gross_profit / gross_loss if gross_loss > 0 else np.inf

    avg_win = wins.mean() if len(wins) else 0
    avg_loss = abs(losses.mean()) if len(losses) else 0

    expectancy = (winrate * avg_win) - ((1-winrate) * avg_loss)

    equity = 1
    for t in trades:
        equity *= (1 + t)

    roi = equity - 1

    return {
        "trades": len(trades),
        "winrate": winrate,
        "profit_factor": pf,
        "expectancy": expectancy,
        "roi": roi,
        "avg_win": avg_win,
        "avg_loss": avg_loss
    }
    
def run_backtest(df, sl=0.07, tp=0.15, fee=0.001):

    signal_trades = backtest_signal(df, fee)
    tp_trades = backtest_tp_sl(df, sl, tp)
    trail_trades = backtest_trailing(df)

    signal_stats = calc_stats(signal_trades)
    tp_stats = calc_stats(tp_trades)
    trail_stats = calc_stats(trail_trades)

    return {
        "signal": signal_stats,
        "tp_sl": tp_stats,
        "trailing": trail_stats
    }