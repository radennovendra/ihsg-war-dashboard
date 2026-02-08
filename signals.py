import pandas as pd
from config import MIN_AVG_VALUE, DISCOUNT_LEVEL, SCORE_VERSION
from broker_style import accumulation_strength



# ==========================
# SAFE SCALAR HELPER
# ==========================
def to_float(x):
    """
    Convert any pandas scalar/Series/object safely into float.
    Bulletproof against Yahoo weird returns.
    """
    try:
        if hasattr(x, "item"):
            return float(x.item())
        return float(x)
    except Exception:
        return None

def safe_div(a, b, default=0):
    """
    Bulletproof division: never crash on zero/None.
    """
    try:
        if b is None or b == 0:
            return default
        return a / b
    except Exception:
        return default

def gap_spike_filter(df):
    """
    Reject stocks with abnormal gap jumps (often noise/manipulation).
    """
    close = df["Close"]
    gap = abs(close.iloc[-1] / close.iloc[-2] - 1)

    if gap > 0.15:  # >15% gap in one day
        return True
    return False

def conviction_tier(score):
    if score >= 85:
        return "TIER-1 ELITE"
    elif score >= 70:
        return "TIER-2 STRONG"
    elif score >= 55:
        return "TIER-3 EARLY"
    elif score >= 40:
        return "TIER-4 WATCH"
    return "TIER-5 NO EDGE"


# ==========================
# ATR ENGINE (STOPLOSS)
# ==========================
def atr(df, period=14):
    tr1 = (df["High"] - df["Low"]).abs()
    tr2 = (df["High"] - df["Close"].shift()).abs()
    tr3 = (df["Low"] - df["Close"].shift()).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    val = tr.rolling(period).mean().iloc[-1]
    return to_float(val)


def entry_and_stop(df):
    close = to_float(df["Close"].iloc[-1])
    a = atr(df)

    if close is None or a is None:
        return None, None, None

    return close - 0.5 * a, close + 0.5 * a, close - 1.5 * a

# ==========================
# TAKE PROFIT
# ==========================
def compute_take_profit(df, entry):

    high = df["High"]
    low = df["Low"]

    # ATR
    atr_val = to_float((high - low).rolling(14).mean().iloc[-1])
    if atr_val is None or atr_val <= 0:
        atr_val = entry * 0.02

    atr = atr_val

    # base targets
    tp1 = entry + 1.5 * atr
    tp2 = entry + 3.0 * atr
    tp3 = entry + 5.0 * atr

    # resistance
    resistance = float(high.rolling(20).max().iloc[-2])

    # ==========================
    # SMART MONEY OVERRIDE
    # ==========================
    if resistance > entry:
        # gunakan resistance sebagai TP2 jika masuk akal
        tp2 = max(tp1 * 1.1, min(tp2, resistance))

    # ==========================
    # ENFORCE ORDER
    # ==========================
    tp_list = sorted([tp1, tp2, tp3])

    tp1 = tp_list[0]
    tp2 = tp_list[1]
    tp3 = tp_list[2]

    # safety: TP1 tidak boleh di bawah entry
    if tp1 <= entry:
        tp1 = entry * 1.02
        tp2 = entry * 1.05
        tp3 = entry * 1.10

    return {
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "resistance": resistance,
        "atr": atr
    }

# ==========================
# COMMON CORE SIGNALS
# ==========================
def core_signals(df):

    if df is None or df.empty:
        return None

    # Fix Yahoo MultiIndex columns (BUMI etc)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if len(df) < 60:
        return None

    close = to_float(df["Close"].iloc[-1])
    if close <= 0 :
        return None
    vol_today = to_float(df["Volume"].iloc[-1])

    avgvol = to_float(df["Volume"].rolling(20).mean().iloc[-2])
    if close is None or vol_today is None or avgvol is None:
        return None

    # ==========================
    # Liquidity Proxy (Ultra Safe)
    # ==========================
    avg_value_series = (df["Close"] * df["Volume"]).rolling(20).mean()
    avg_value = to_float(avg_value_series.iloc[-2])

    if avg_value is None:
        return None

    liquidity_penalty = bool(avg_value < MIN_AVG_VALUE)

    broker_accum = bool(accumulation_strength(df))

    # ==========================
    # Value proxy discount
    # ==========================
    high_52w = to_float(df["Close"].max())
    if high_52w is None or high_52w == 0:
        return None

    discount_52w = float((close / high_52w) - 1)
    undervalued_proxy = discount_52w < DISCOUNT_LEVEL

    # ==========================
    # Compression
    # ==========================
    high20 = to_float(df["High"].rolling(20).max().iloc[-1])
    low20 = to_float(df["Low"].rolling(20).min().iloc[-1])

    if high20 is None or low20 is None or low20 == 0:
        return None

    compression = ((high20 / low20) - 1) < 0.15

    # Capitulation spike
    capitulation = vol_today > 2.0 * avgvol

    # ==========================
    # Absorption candle
    # ==========================
    high_today = to_float(df["High"].iloc[-1])
    low_today = to_float(df["Low"].iloc[-1])

    if high_today is None or low_today is None:
        return None

    candle_range = high_today - low_today

    absorption = (
        vol_today > 1.7 * avgvol
        and candle_range < close * 0.025
    )

    # ==========================
    # Breakout confirm
    # ==========================
    prev_high20 = to_float(df["Close"].rolling(20).max().iloc[-2])
    if prev_high20 is None:
        return None

    breakout_confirm = close > prev_high20 and vol_today > 2.0 * avgvol

    # Multi accumulation
    multi_accum = int((df["Volume"].tail(5) > avgvol).sum()) >= 2

    return {
        "close": close,
        "vol_today": vol_today,
        "avgvol": avgvol,
        "avg_value": avg_value,
        "liquidity_penalty": liquidity_penalty,
        "broker_accum": broker_accum,
        "discount_52w": discount_52w,
        "undervalued_proxy": undervalued_proxy,
        "compression": compression,
        "capitulation": capitulation,
        "absorption": absorption,
        "breakout_confirm": breakout_confirm,
        "multi_accum": multi_accum,
    }


# ==========================
# V1 BASIC SCORE
# ==========================
def evaluate_v1(df):
    s = core_signals(df)
    if s is None:
        return None

    score = 0
    if s["breakout_confirm"]:
        score += 40
    if s["absorption"]:
        score += 20
    if s["multi_accum"]:
        score += 15
    if s["undervalued_proxy"] and s["compression"]:
        score += 20
    if s["broker_accum"]:
        score += 15
    if s["capitulation"] and s["undervalued_proxy"]:
        score += 10

    if s["liquidity_penalty"]:
        score -= 15

    entry_low, entry_high, stop = entry_and_stop(df)

    return {
        "score": max(score, 0),
        "discount_52w": s["discount_52w"],
        "absorption": s["absorption"],
        "broker_accum": s["broker_accum"],
        "multi_accum": s["multi_accum"],
        "entry_low": entry_low,
        "entry_high": entry_high,
        "stoploss": stop,
    }


# ==========================
# V2 INSTITUTIONAL LEADER
# ==========================
def evaluate_v2(df, ihsg_df):
    base = evaluate_v1(df)
    if base is None:
        return None

    score = base["score"]

    try:
        stock_ret = float(
            df["Close"].iloc[-1].item() / 
            df["Close"].iloc[-21].item() 
            - 1
        )
        idx_ret = float(
            ihsg_df["Close"].iloc[-1].item() / 
            ihsg_df["Close"].iloc[-21].item() 
            - 1
        )

        rs = stock_ret - idx_ret
    except Exception:
        rs = 0

    if rs > 0.03:
        score += 10
    if rs > 0.07:
        score += 20

    ma20 = df["Close"].rolling(20).mean().iloc[-1]
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    trend_ok = bool(ma20 > ma50)

    if trend_ok:
        score += 10

    base["score"] = max(score, 0)
    base["trend_ok"] = trend_ok
    base["relative_strength"] = rs
    return base


# ==========================
# V3 QUANT FUND MODEL
# ==========================
def evaluate_v3(df, ihsg_df):
    base = evaluate_v2(df, ihsg_df)
    if base is None:
        return None

    score = base["score"]

    # Momentum 3M
    try:
        ret3m = float(
            df["Close"].iloc[-1].item()
            / df["Close"].iloc[-60].item()
            - 1
        )
    except Exception:
        ret3m = 0

    if ret3m > 0.25:
        score += 20
    elif ret3m > 0.10:
        score += 10

    # Sharpe proxy
    returns = df["Close"].pct_change().dropna()
    if len(returns) > 30:
        std = returns.std()
        
        if std is not None and std > 0:
            sharpe = returns.mean() / std
        else:
            sharpe = 0

        if sharpe > 0.15:
            score += 15
        elif sharpe > 0.08:
            score += 8

    # Drawdown control
    peak = to_float(df["Close"].max())

    if peak is None or peak == 0:
        return None

    dd = float(df["Close"].iloc[-1].item() / peak - 1)

    if dd < -0.50:
        score -= 25
    elif dd < -0.35:
        score -= 15

    base["score"] = float(max(score, 0))
    base["momentum3m"] = ret3m
    base["drawdown"] = dd

    # ==========================
    # TAKE PROFIT ENGINE (NEW)
    # ==========================
    entry_price = base["entry_high"]  # pakai entry tengah

    tp = compute_take_profit(df, entry_price)

    base["tp1"] = tp["tp1"]
    base["tp2"] = tp["tp2"]
    base["tp3"] = tp["tp3"]
    base["resistance"] = tp["resistance"]
    base["atr"] = tp["atr"]

    return base

# ==========================
# V4 ALPHA MODEL
# ==========================
def evaluate_v4(df, ihsg_df):

    base = evaluate_v3(df, ihsg_df)
    if base is None:
        return None

    # Noise filter only
    if gap_spike_filter(df):
        return None

    return base

# ==========================
# MAIN SELECTOR
# ==========================
def evaluate(df, ihsg_df=None):

    if SCORE_VERSION == "v1":
        return evaluate_v1(df)

    if SCORE_VERSION == "v2":
        return evaluate_v2(df, ihsg_df)

    if SCORE_VERSION == "v3":
        return evaluate_v3(df, ihsg_df)

    if SCORE_VERSION == "v4":
        return evaluate_v4(df, ihsg_df)

    return evaluate_v3(df, ihsg_df)

