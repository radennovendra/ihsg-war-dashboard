import yfinance as yf

def foreign_flow_proxy():
    """
    Proxy foreign risk regime using:
    - EIDO ETF trend
    - USDIDR pressure
    """

    eido = yf.download("EIDO", period="1mo")
    idr  = yf.download("IDR=X", period="1mo")

    eido_ret5 = (eido["Close"].iloc[-1] /
                 eido["Close"].iloc[-6]) - 1

    idr_ret5 = (idr["Close"].iloc[-1] /
                idr["Close"].iloc[-6]) - 1

    if eido_ret5 < -0.03 and idr_ret5 > 0.02:
        return "FOREIGN OUT"
    elif eido_ret5 > 0.02:
        return "FOREIGN IN"
    else:
        return "NEUTRAL"
