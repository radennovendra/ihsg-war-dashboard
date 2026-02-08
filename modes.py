def score_value_mode(f):
    """
    PBV + ROE combo (Indonesia strongest undervaluation proxy)
    """
    if f is None:
        return False

    return (f["pbv"] < 1.5) and (f["roe"] > 0.12)


def score_growth_mode(f):
    """
    PER cheap + EPS growth
    """
    if f is None:
        return False

    return (f["per"] < 15) and (f["eps_growth"] > 0.10)


def score_dividend_mode(f):
    """
    Dividend yield defensive
    """
    if f is None:
        return False

    return (f["div_yield"] > 0.04) and (f["pbv"] < 2.0)


def score_magic_formula(f):
    """
    Joel Greenblatt proxy:
    Cheap + High ROE
    """
    if f is None:
        return False

    return (f["per"] < 15) and (f["roe"] > 0.15)


def score_turnaround_mode(f):
    """
    Deep value turnaround:
    Very cheap PBV + positive growth
    """
    if f is None:
        return False

    return (f["pbv"] < 1.0) and (f["eps_growth"] > 0.0)
