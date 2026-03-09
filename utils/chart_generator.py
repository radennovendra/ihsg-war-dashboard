import os
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import numpy as np
import matplotlib.pyplot as plt
import time
from utils.yahoo_pro import download_price

os.makedirs("charts", exist_ok=True)

def generate_chart(sym, r):

    time.sleep(0.1)

    file = f"charts/{sym}.png"

    try:
        df = None

        for _ in range(3):
            
            df = download_price(sym)
            
            if df is not None and not df.empty:
                break
            
            time.sleep(0.1)

        if df is None or df.empty:
            return None

        if len(df) < 25:
            return None
        
        required_cols = ["Open", "High", "Low", "Close", "Volume"]

        for c in required_cols:
            if c not in df.columns:
                return None
            if df[c].dropna().empty:
                return None

        df = df.tail(60)

        df = df[["Open", "High", "Low", "Close", "Volume"]]

        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        df = df.dropna()

        if df.empty or len(df) < 20:
            return None
        
        if df["High"].dropna().shape[0] == 0:
            return None 
        if df["Low"].dropna().shape[0] == 0:
            return None

        # =========================
        # INDICATORS
        # =========================

        df.loc[:, "MA20"] = df["Close"].rolling(20).mean()
        df.loc[:, "MA50"] = df["Close"].rolling(50, min_periods=10).mean()
        df.loc[:, "EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()

        # VWAP
        typical = (df["High"] + df["Low"] + df["Close"]) / 3
        df.loc[:, "VWAP"] = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()

        # Breakout level
        high_series = df["High"].dropna()
        low_series = df["Low"].dropna()

        if len(high_series) < 5 or len(low_series) < 5:
            return None
            
        breakout = high_series.tail(20).max()
        last_close = float(df["Close"].iloc[-1])

        breakout_label = ""

        if last_close >= breakout:
            breakout_label = "BREAKOUT"
        elif last_close >= breakout * 0.98:
            breakout_label = "NEAR BREAKOUT"

        # Smart money zone
        zone_high = breakout
        zone_low = low_series.tail(20).min()

        # =========================
        # VOLUME SPIKE
        # =========================

        avg_vol = float(df["Volume"].rolling(20, min_periods=1).mean().iloc[-1])
        last_vol = float(df["Volume"].iloc[-1])

        vol_ratio = last_vol / avg_vol if avg_vol > 0 else 1

        vol_label = ""
        if vol_ratio > 2:
            vol_label = f"⚡VOL {vol_ratio:.1f}x"
        
        vol_series = pd.Series(np.nan, index=df.index)

        vol_marker = None

        if vol_ratio > 2:
            vol_series.iloc[-1] = df["High"].iloc[-1]*1.01

            vol_marker = mpf.make_addplot(
                vol_series,
                type='scatter',
                markersize=120,
                marker='o',
                color='yellow'
                )

        # =========================
        # BUY / SELL SIGNAL
        # =========================

        cross_up = (
            (df["EMA9"] > df["MA20"]) &
            (df["EMA9"].shift(1) <= df["MA20"].shift(1))
        )

        cross_down = (
            (df["EMA9"] < df["MA20"]) &
            (df["EMA9"].shift(1) >= df["MA20"].shift(1))
        )

        buy = (df["Low"] * 0.98).where(cross_up)
        sell = (df["High"] * 1.02).where(cross_down)

        buy_plot = mpf.make_addplot(
            buy,
            type='scatter',
            marker='^',
            color='lime',
            markersize=120
        )

        sell_plot = mpf.make_addplot(
            sell,
            type='scatter',
            marker='v',
            color='red',
            markersize=120
        )
        # =========================
        # ENTRY / SL / TP
        # =========================

        entry_low = float(r["entry_low"])
        entry_high = float(r["entry_high"])
        sl = float(r["stoploss"])
        tp = float(r["tp2"])
        breakout = float(breakout)

        # =========================
        # FOREIGN FORMAT
        # =========================

        foreign = r.get("foreign_net",0)

        if abs(foreign) >= 1e9:
            ftxt = f"{foreign/1e9:.1f}B"
        elif abs(foreign) >= 1e6:
            ftxt = f"{foreign/1e6:.1f}M"
        else:
            ftxt = str(int(foreign))

        # =========================
        # ADDPLOTS
        # ========================= 

        apds = [

            mpf.make_addplot(df["MA20"], color='blue'),
            mpf.make_addplot(df["MA50"], color='orange'),
            mpf.make_addplot(df["VWAP"], color='purple'),
            mpf.make_addplot(df["EMA9"], color='white'),

            buy_plot,
            sell_plot,
        ]

        if vol_marker:
            apds.append(vol_marker)

        # =========================
        # HLINES
        # =========================

        hlines = dict(
            hlines=[entry_low, entry_high, sl, tp, breakout, zone_high, zone_low],
            colors=['yellow','yellow','red','green','cyan', 'grey', 'grey'],
            linestyle='-'
        )
        # =========================
        # TITLE
        # =========================
        
        trend = ""

        if df["EMA9"].iloc[-1] > df["MA20"].iloc[-1] > df["MA50"].iloc[-1]:
            trend = "STRONG UPTREND"
        elif df["EMA9"].iloc[-1] < df["MA20"].iloc[-1] < df["MA50"].iloc[-1]:
            trend = "DOWNTREND"
        else:
            trend = "SIDEWAYS"

        title = (
            f"{sym} | Score {r['score']} | {trend} | Foreign {ftxt}\n"
            f"Entry {int(entry_low)}-{int(entry_high)}  "
            f"SL {int(sl)}  TP {int(tp)}  "
            f"{vol_label} {breakout_label}"
        )

        # =========================
        # STYLE
        # =========================

        style = mpf.make_mpf_style(
            base_mpf_style='nightclouds',
            y_on_right=True,
            gridstyle='--',
            facecolor='#0f172a',
            figcolor='#0f172a'
        )

        # =========================
        # PLOT
        # =========================

        if df["Close"].dropna().shape[0] < 5:
            return None
        if any(np.isnan([entry_low, entry_high, sl, tp])):
            return None
        fig, axlist = mpf.plot(
            df,
            type='candle',
            style=style,
            addplot=apds,
            volume=True,
            title=title,
            hlines=hlines,
            returnfig=True,
            figsize=(11,7),
            fill_between=dict(y1=entry_low, y2=entry_high, alpha=0.08, color='yellow')
        )

        ax = axlist[0]

        legend_items = ["MA20", "MA50", "VWAP", "EMA9", "BUY", "SELL"]

        if vol_marker:
            legend_items.append("VOLUME SPIKE")

        ax.legend(legend_items, loc="upper left")
        
        fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.08)
        fig.savefig(file)
        plt.close(fig)

        return file

    except Exception as e:

        print("Chart error:", e)
        return None