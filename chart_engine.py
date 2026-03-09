import yfinance as yf
import matplotlib.pyplot as plt
import os

os.makedirs("charts", exist_ok=True)

def generate_chart(symbol):

    df = yf.download(symbol, period="6mo", progress=False)

    plt.figure(figsize=(6,4))
    plt.plot(df["Close"])
    plt.title(symbol)

    path = f"charts/{symbol}.png"
    plt.savefig(path)
    plt.close()

    return path