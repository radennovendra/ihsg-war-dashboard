import os
import time
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

from utils.yahoo_pro import download_price
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

MA20_COLOR = "#ffffff"
MA30_COLOR = "#b388ff"
VWAP_COLOR = "#ffd166"
EMA9_COLOR = "#3a86ff"

BUY_COLOR = "#00ff88"
SELL_COLOR = "#ff4d4d"

ENTRY_ZONE_COLOR = "#ffd166"
ACC_ZONE_COLOR = "#00e5ff"

SL_COLOR = "#ff4d4d"
TP_COLOR = "#00ff88"

os.makedirs("charts", exist_ok=True)


def generate_chart(sym, r):

    file = f"charts/{sym}.png"

    try:

        # =========================
        # DOWNLOAD PRICE
        # =========================

        df = None

        for _ in range(3):

            try:
                df = download_price(sym)

                if df is not None and not df.empty:
                    break

            except:
                pass

            time.sleep(0.05)

        if df is None or df.empty:
            return None


        # =========================
        # BASIC CLEANING
        # =========================

        cols = ["Open","High","Low","Close","Volume"]

        if not all(c in df.columns for c in cols):
            return None

        df = df[cols].copy()

        for c in cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")

        df = df.dropna()

        if df.empty:
            return None

        df.index = pd.to_datetime(df.index)

        # =========================
        # USE LAST 1 MONTH
        # =========================

        df = df.tail(30)

        if len(df) < 10:
            return None


        # =========================
        # VALIDATION
        # =========================

        if df["High"].isna().all():
            return None

        if df["Low"].isna().all():
            return None

        if df["Close"].isna().all():
            return None


        # =========================
        # INDICATORS
        # =========================

        df["MA20"] = df["Close"].rolling(20).mean()

        df["MA30"] = df["Close"].rolling(30, min_periods=10).mean()

        df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()

        typical = (df["High"] + df["Low"] + df["Close"]) / 3

        df["VWAP"] = (typical * df["Volume"]).cumsum() / df["Volume"].cumsum()


        # =========================
        # BREAKOUT ZONE
        # =========================

        window = df.tail(20)

        if window.empty:
            return None

        breakout = float(window["High"].max())

        zone_low = float(window["Low"].min())

        last_close = float(df["Close"].iloc[-1])

        breakout_label = ""

        if last_close >= breakout:
            breakout_label = "BREAKOUT"

        elif last_close >= breakout * 0.98:
            breakout_label = "NEAR BREAKOUT"


        # =========================
        # BUY SELL SIGNAL
        # =========================
        buy = pd.Series(np.nan, index=df.index)
        sell = pd.Series(np.nan, index=df.index)

        # ========================
        # 1 EMA CROSS
        # ========================

        cross_up = (
            (df["EMA9"] > df["MA20"]) &
            (df["EMA9"].shift(1) <= df["MA20"].shift(1))
        )

        buy[cross_up] = df["Low"] * 0.98


        cross_down = (
            (df["EMA9"] < df["MA20"]) &
            (df["EMA9"].shift(1) >= df["MA20"].shift(1))
        )

        sell[cross_down] = df["High"] * 1.02


        # ========================
        # 2 EMA PULLBACK
        # ========================

        pullback_buy = (
            (df["Close"] > df["MA20"]) &
            (df["Low"] <= df["EMA9"])
        )

        buy[pullback_buy] = df["Low"] * 0.98


        pullback_sell = (
            (df["Close"] < df["MA20"]) &
            (df["High"] >= df["EMA9"])
        )

        sell[pullback_sell] = df["High"] * 1.02


        # ========================
        # 3 VWAP RECLAIM
        # ========================

        vwap_buy = (
            (df["Close"] > df["VWAP"]) &
            (df["Close"].shift(1) <= df["VWAP"].shift(1))
        )

        buy[vwap_buy] = df["Low"] * 0.98


        vwap_sell = (
            (df["Close"] < df["VWAP"]) &
            (df["Close"].shift(1) >= df["VWAP"].shift(1))
        )

        sell[vwap_sell] = df["High"] * 1.02


        # ========================
        # 4 MOMENTUM CANDLE
        # ========================

        momentum_buy = (
            (df["Close"] > df["Open"]) &
            (df["Close"] > df["High"].shift(1))
        )

        buy[momentum_buy] = df["Low"] * 0.98


        momentum_sell = (
            (df["Close"] < df["Open"]) &
            (df["Close"] < df["Low"].shift(1))
        )

        sell[momentum_sell] = df["High"] * 1.02


        buy_plot = mpf.make_addplot(
            buy,
            type="scatter",
            marker="^",
            color=BUY_COLOR,
            markersize=120
        )

        sell_plot = mpf.make_addplot(
            sell,
            type="scatter",
            marker="v",
            color=SELL_COLOR,
            markersize=120
        )


        # =========================
        # ENTRY SL TP
        # =========================

        entry_low = float(r["entry_low"])
        entry_high = float(r["entry_high"])
        sl = float(r["stoploss"])
        tp = float(r["tp2"])

        if any(np.isnan([entry_low,entry_high,sl,tp])):
            return None


        # =========================
        # FOREIGN FLOW TEXT
        # =========================

        foreign = r.get("foreign_net",0)

        if abs(foreign) >= 1e9:
            ftxt = f"{foreign/1e9:.1f}B"

        elif abs(foreign) >= 1e6:
            ftxt = f"{foreign/1e6:.1f}M"

        else:
            ftxt = str(int(foreign))


        # =========================
        # TREND
        # =========================

        trend = "SIDEWAYS"

        if df["EMA9"].iloc[-1] > df["MA20"].iloc[-1] > df["MA30"].iloc[-1]:
            trend = "STRONG UPTREND"

        elif df["EMA9"].iloc[-1] < df["MA20"].iloc[-1] < df["MA30"].iloc[-1]:
            trend = "DOWNTREND"


        # =========================
        # TITLE
        # =========================

        title = (
            f"{sym} | Score {r['score']} | {trend} | Foreign {ftxt}\n"
            f"Entry {int(entry_low)}-{int(entry_high)} "
            f"SL {int(sl)} TP {int(tp)} "
            f"{breakout_label}"
        )


        # =========================
        # ADDPLOTS
        # =========================

        apds = []

        if df["MA20"].notna().sum() > 3:
            apds.append(mpf.make_addplot(df["MA20"], color=MA20_COLOR))

        if df["MA30"].notna().sum() > 3:
            apds.append(mpf.make_addplot(df["MA30"], color=MA30_COLOR))

        if df["VWAP"].notna().sum() > 3:
            apds.append(mpf.make_addplot(df["VWAP"], color=VWAP_COLOR))

        if df["EMA9"].notna().sum() > 3:
            apds.append(mpf.make_addplot(df["EMA9"], color=EMA9_COLOR))

        if buy.notna().sum() > 0:
            apds.append(buy_plot)

        if sell.notna().sum() > 0:
            apds.append(sell_plot)


        # =========================
        # PRICE RANGE
        # =========================

        high_val = df["High"].max()

        low_val = df["Low"].min()

        price_max = max(high_val,tp) * 1.08

        price_min = min(low_val,sl) * 0.95


        # =========================
        # STYLE
        # =========================

        style = mpf.make_mpf_style(
            base_mpf_style="nightclouds",
            y_on_right=True,
            gridstyle="--",
            facecolor="#0f172a",
            figcolor="#0f172a"
        )


        # =========================
        # PLOT
        # =========================

        fig, axlist = mpf.plot(
            df,
            type="candle",
            style=style,
            addplot=apds if len(apds)>0 else None,
            volume=True,
            title=title,
            hlines=dict(
                hlines=[entry_low,entry_high,sl,tp,breakout,zone_low],
                colors=[ENTRY_ZONE_COLOR,ENTRY_ZONE_COLOR,SL_COLOR,TP_COLOR,ACC_ZONE_COLOR,"grey"]
            ),
            returnfig=True,
            figsize=(12,8),
            ylim=(price_min,price_max),
            fill_between=dict(
                y1=entry_low,
                y2=entry_high,
                alpha=0.15,
                color=ENTRY_ZONE_COLOR
            )
        )

        ax = axlist[0]

        ax.axhspan(
            zone_low,
            breakout,
            alpha=0.08,
            color=ACC_ZONE_COLOR
        )

        legend_items = [
            Line2D([0],[0],color=MA20_COLOR,lw=2,label="MA20"),
            Line2D([0],[0],color=MA30_COLOR,lw=2,label="MA30"),
            Line2D([0],[0],color=VWAP_COLOR,lw=2,label="VWAP"),
            Line2D([0],[0],color=EMA9_COLOR,lw=2,label="EMA9"),

            Line2D([0],[0],marker="^",color=BUY_COLOR,lw=0,label="BUY",markersize=10),
            Line2D([0],[0],marker="v",color=SELL_COLOR,lw=0,label="SELL",markersize=10),

            Line2D([0],[0],color=SL_COLOR,lw=2, label="STOP LOSS"),
            Line2D([0],[0],color=TP_COLOR,lw=2, label="TAKE PROFIT"),

            Patch(color=ENTRY_ZONE_COLOR,alpha=0.15,label="ENTRY ZONE"),
            Patch(color=ACC_ZONE_COLOR,alpha=0.08,label="ACCUMULATION ZONE")
        ]

        ax.legend(
            handles=legend_items,
            loc="upper left",
            fontsize=9,
            frameon=True,
            facecolor="#111827",
            edgecolor="gray"
        )

        fig.subplots_adjust(left=0.06, right=0.96, top=0.90, bottom=0.08)
        fig.savefig(file,dpi=160, bbox_inches="tight")

        plt.close(fig)

        return file

    except Exception as e:

        print(f"Chart error {sym}: {e}")

        return None