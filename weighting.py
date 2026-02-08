def portfolio_weights(regime, sectors):
    """
    Portfolio allocation weights depending on market regime.

    Returns dict:
    {sector: weight%, CASH: weight%}
    """

    weights = {}

    # ============================
    # PANIC MODE
    # ============================
    if regime == "PANIC":
        # Survival mode: mostly cash
        cash = 70
        remain = 30

        if len(sectors) > 0:
            per = remain // len(sectors)
            for s in sectors:
                weights[s] = per

        weights["CASH"] = cash
        return weights

    # ============================
    # RISK-OFF MODE
    # ============================
    if regime == "RISK-OFF":
        cash = 40
        remain = 60

        if len(sectors) > 0:
            per = remain // len(sectors)
            for s in sectors:
                weights[s] = per

        weights["CASH"] = cash
        return weights

    # ============================
    # NEUTRAL MODE
    # ============================
    if regime == "NEUTRAL":
        cash = 20
        remain = 80

        if len(sectors) > 0:
            # leader gets bigger weight
            weights[sectors[0]] = 40
            if len(sectors) > 1:
                weights[sectors[1]] = 25
            if len(sectors) > 2:
                weights[sectors[2]] = 15

        weights["CASH"] = cash
        return weights

    # ============================
    # RISK-ON MODE
    # ============================
    if regime == "RISK-ON":
        cash = 10
        remain = 90

        if len(sectors) > 0:
            weights[sectors[0]] = 50
            if len(sectors) > 1:
                weights[sectors[1]] = 25
            if len(sectors) > 2:
                weights[sectors[2]] = 15

        weights["CASH"] = cash
        return weights

    return {"CASH": 100}
