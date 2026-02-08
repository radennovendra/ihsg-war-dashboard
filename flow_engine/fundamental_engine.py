import yfinance as yf

# ==========================
# SAFE GET
# ==========================
def safe(x, default=0):
    try:
        if x is None:
            return default
        return float(x)
    except:
        return default

# ==========================
# MAIN FUNDAMENTAL
# ==========================
def get_fundamental(sym):
    """
    Balanced fund model:
    quality + growth + value
    """

    try:
        t = yf.Ticker(sym)
        info = t.info
    except:
        return {
            "fund_score": 0,
            "quality": "UNKNOWN"
        }

    # ======================
    # CORE METRICS
    # ======================
    roe = safe(info.get("returnOnEquity"))
    growth = safe(info.get("revenueGrowth"))
    eps_growth = safe(info.get("earningsGrowth"))
    margin = safe(info.get("profitMargins"))
    debt = safe(info.get("debtToEquity"))
    pe = safe(info.get("trailingPE"))
    pbv = safe(info.get("priceToBook"))
    eps = safe(info.get("trailingEps"))
    der = debt

    score = 0

    # ======================
    # QUALITY
    # ======================
    if roe > 0.15:
        score += 8
    elif roe > 0.10:
        score += 5

    if margin > 0.15:
        score += 5

    # ======================
    # GROWTH
    # ======================
    if growth > 0.15:
        score += 8
    elif growth > 0.05:
        score += 5

    if eps_growth > 0.15:
        score += 6

    # ======================
    # DEBT
    # ======================
    if debt > 0 and debt < 1:
        score += 5
    elif debt > 2:
        score -= 5

    # ======================
    # VALUE
    # ======================
    if pe > 0 and pe < 12:
        score += 5
    elif pe > 40:
        score -= 5

    # clamp
    score = max(min(score, 40), -10)

    # quality label
    if score >= 25:
        q = "HIGH"
    elif score >= 10:
        q = "MID"
    else:
        q = "LOW"

    return {
        "fund_score": score,
        "quality": q,
        "roe": roe,
        "growth": growth,
        "eps_growth": eps_growth,
        "margin": margin,
        "debt": debt,
        "der": der,
        "pbv": pbv,
        "eps": eps,
        "pe": pe
    }