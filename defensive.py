# ================================
# Defensive Sector Rules (IDX Proxy)
# ================================

DEFENSIVE_SECTORS = [
    "CONSUMER",
    "CONSUMER NON-CYCLICAL",
    "HEALTHCARE",
    "UTILITIES",
    "TELECOMMUNICATIONS",
    "TELCO",
]

CYCLICAL_SECTORS = [
    "ENERGY",
    "MATERIALS",
    "INDUSTRIALS",
    "PROPERTY",
    "TECHNOLOGY",
]


def allowed_sectors(regime, top_sectors):
    """
    Adjust sector allocation depending on market regime.
    """

    # PANIC: Only defensive sectors
    if regime == "PANIC":
        return [s for s in top_sectors if any(d in s for d in DEFENSIVE_SECTORS)]

    # RISK-OFF: Prefer defensive, allow 1 strong leader cyclical
    if regime == "RISK-OFF":
        defensive = [s for s in top_sectors if any(d in s for d in DEFENSIVE_SECTORS)]
        if len(defensive) >= 2:
            return defensive[:2]

        # fallback allow strongest sector anyway
        return top_sectors[:1]

    # Neutral / Risk-On: allow normal rotation
    return top_sectors
