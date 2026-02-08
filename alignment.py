def is_value_flow_alignment(res):
    """
    Ultra rare institutional alignment:
    Deep Discount + Smart Money Absorption
    """

    # Flow requirement
    if not res.get("absorption"):
        return False

    if res["score"] < 75:
        return False

    # Value proxy requirement
    if not res.get("undervalued_proxy"):
        return False

    return True


def format_alignment_alert(sym, res, regime):
    """
    Telegram message for Value Proxy Alignment.
    """

    msg = f"""🔥 ULTRA RARE VALUE+FLOW SIGNAL

Symbol: {sym}
Sector: {res['sector']}
Regime: {regime}

SMART MONEY FLOW:
Absorption: ✅
Score: {res['score']}/100
Multi-Accum: {res['multi_accum']}

VALUE PROXY:
Discount vs 52W High: {res['discount_52w']:.1%}
Compression Base: {res['compression']}
Capitulation Spike: {res['capitulation']}

Setup:
Mean Reversion Candidate: {res['mean_reversion']}

🏛️ Meaning:
Deep discount + Smart Money Accumulation
(Extremely rare reversal zone)
"""

    return msg
