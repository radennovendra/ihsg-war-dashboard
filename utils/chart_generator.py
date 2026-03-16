import os
import time
import numpy as np
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

from utils.yahoo_pro import download_price
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib
from PIL import Image


Image.MAX_IMAGE_PIXELS = None
matplotlib.use("Agg")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["savefig.dpi"] = 120
plt.rcParams["lines.antialiased"] = True
plt.rcParams.update({
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9
})

matplotlib.rcParams['font.family'] = 'DejaVu Sans'

EMA9_COLOR = "#3a86ff"
EMA21_COLOR = "#ff9f1c"
MA50_COLOR = "#b388ff"
VWAP_COLOR = "#ffd166"

BUY_COLOR = "#00ff88"
SELL_COLOR = "#ff4d4d"

ENTRY_ZONE_COLOR = "#f59e0b"
ACC_ZONE_COLOR = "#06b6d4"

SL_COLOR = "#ff4d4d"
TP_COLOR = "#00ff88"

os.makedirs("charts", exist_ok=True)

IHSG_DATA = download_price("^JKSE")

if IHSG_DATA is None or IHSG_DATA.empty:
    IHSG_DATA = pd.DataFrame()

def generate_chart(sym, r, df):

    sym_clean = sym.replace(".JK","")
    file = f"charts/{sym_clean}.png"

    # chart cache
    if os.path.exists(file):
        age = time.time() - os.path.getmtime(file)
        if age < 3600:
            return file

    print("Generating chart:", sym)

    try:

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

        df = df.tail(200)

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

        df["EMA21"] = df["Close"].ewm(span=21, adjust=False).mean()

        df["MA50"] = df["Close"].rolling(50).mean()

        df["EMA9"] = df["Close"].ewm(span=9, adjust=False).mean()

        typical = (df["High"] + df["Low"] + df["Close"]) / 3

        df["VWAP"] = ((typical * df["Volume"]).rolling(20).sum() / df["Volume"].rolling(20).sum())

        trend_up = df["EMA9"] > df["EMA21"]
        trend_down = df["EMA9"] < df["EMA21"]

        vol_confirm = df["Volume"] > df["Volume"].rolling(20).mean()

        # =========================
        # ATR
        # =========================

        df["ATR"] = (
            pd.concat([
                df["High"] - df["Low"],
                abs(df["High"] - df["Close"].shift()),
                abs(df["Low"] - df["Close"].shift())
            ], axis=1).max(axis=1)
        ).rolling(14).mean()

        volatility_ok = df["ATR"] > df["Close"] * 0.01

        # =========================
        # Relative Strength vs IHSG
        # =========================
        if not IHSG_DATA.empty:
            ihsg = IHSG_DATA["Close"].pct_change().rolling(20).sum()
            ihsg = ihsg.reindex(df.index).ffill()
        else:
            ihsg = pd.Series(0, index=df.index)

        ihsg_ma = ihsg.rolling(50).mean()

        market_bull = ihsg > ihsg_ma

        stock_rs = df["Close"].pct_change().rolling(20).sum()

        rs_strength = stock_rs > ihsg
        rs_label = "RS STRONG" if rs_strength.iloc[-1] else "RS WEAK"

        # =========================
        # Liquidity Filter
        # =========================

        df["Value"] = df["Close"] * df["Volume"]

        liquid = df["Value"].rolling(20).mean() > 20_000_000_000

        # =========================
        # Accumulation Detector
        # =========================

        df["Range"] = df["High"] - df["Low"]

        volatility_contract = (
            df["Range"].rolling(10).mean() <
            df["Range"].rolling(50).mean()
        )

        # =========================
        # BREAKOUT ZONE
        # =========================

        window = df.tail(60)

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
            (df["EMA9"] > df["EMA21"]) &
            (df["EMA9"].shift(1) <= df["EMA21"].shift(1))
        )

        cross_down = (
            (df["EMA9"] < df["EMA21"]) &
            (df["EMA9"].shift(1) >= df["EMA21"].shift(1))
        )

        # ========================
        # 2 EMA PULLBACK
        # ========================

        pullback_buy = (
            (df["Close"] > df["EMA21"]) &
            (df["Low"] <= df["EMA9"])
        )

        pullback_sell = (
            (df["Close"] < df["EMA21"]) &
            (df["High"] >= df["EMA9"])
        )

        # ========================
        # 3 VWAP RECLAIM
        # ========================

        vwap_buy = (
            (df["Close"] > df["VWAP"]) &
            (df["Close"].shift(1) <= df["VWAP"].shift(1))
        )

        vwap_sell = (
            (df["Close"] < df["VWAP"]) &
            (df["Close"].shift(1) >= df["VWAP"].shift(1))
        )

        # ========================
        # 4 MOMENTUM CANDLE
        # ========================

        momentum_buy = (
            (df["Close"] > df["Open"]) &
            (df["Close"] > df["High"].shift(1)) &
            (df["Volume"] > df["Volume"].rolling(20).mean()*1.2)
        )

        momentum_sell = (
            (df["Close"] < df["Open"]) &
            (df["Close"] < df["Low"].shift(1))
        )

        # PRIORITY SYSTEM

        # 1 MOMENTUM
        buy[momentum_buy & trend_up & vol_confirm & volatility_ok & rs_strength & liquid] = df["Low"] * 0.97

        # 2 VWAP RECLAIM
        buy[vwap_buy & buy.isna() & vol_confirm & rs_strength & liquid] = df["Low"] * 0.97

        # 3 EMA CROSS
        buy[cross_up & buy.isna() & trend_up & rs_strength & liquid] = df["Low"] * 0.97

        # 4 EMA PULLBACK
        buy[pullback_buy & buy.isna() & trend_up & volatility_contract & rs_strength & liquid] = df["Low"] * 0.97


        # SELL SIDE
        sell[momentum_sell & trend_down & vol_confirm] = df["High"] * 1.03
        sell[vwap_sell & sell.isna() & vol_confirm] = df["High"] * 1.03
        sell[cross_down & sell.isna() & trend_down] = df["High"] * 1.03
        sell[pullback_sell & sell.isna() & trend_down] = df["High"] * 1.03
        
        buy = buy
        sell = sell
        
        chart_df = df.tail(20).copy()

        buy_chart = buy.loc[chart_df.index]
        sell_chart = sell.loc[chart_df.index]

        buy_chart = buy_chart.replace(0, np.nan)
        sell_chart = sell_chart.replace(0, np.nan)

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

        if df["EMA9"].iloc[-1] > df["EMA21"].iloc[-1] > df["MA50"].iloc[-1]:
            trend = "STRONG UPTREND"

        elif df["EMA9"].iloc[-1] < df["EMA21"].iloc[-1] < df["MA50"].iloc[-1]:
            trend = "DOWNTREND"
        
        # =========================
        # Score Engine
        # =========================

        score = 0

        if trend_up.iloc[-1]:
            score += 2

        if vol_confirm.iloc[-1]:
            score += 2

        if rs_strength.iloc[-1]:
            score += 2

        if volatility_ok.iloc[-1]:
            score += 2
        
        if volatility_contract.iloc[-1]:
            score += 2
        
        if liquid.iloc[-1]:
            score += 2

        if breakout_label == "BREAKOUT":
            score += 2

        # =========================
        # TITLE
        # =========================

        title = (
            f"{sym} | {trend} | {rs_label}\n"
            f"Entry {int(entry_low)}-{int(entry_high)} | SL {int(sl)} | TP {int(tp)}"
        )
        # =========================
        # ADDPLOTS
        # =========================

        apds = []

        if chart_df["EMA21"].notna().sum() > 3:
            apds.append(mpf.make_addplot(chart_df["EMA21"], color=EMA21_COLOR))

        if chart_df["MA50"].notna().sum() > 3:
            apds.append(mpf.make_addplot(chart_df["MA50"], color=MA50_COLOR))

        if chart_df["VWAP"].notna().sum() > 3:
            apds.append(mpf.make_addplot(chart_df["VWAP"], color=VWAP_COLOR))

        if chart_df["EMA9"].notna().sum() > 3:
            apds.append(mpf.make_addplot(chart_df["EMA9"], color=EMA9_COLOR))


        # =========================
        # PRICE RANGE
        # =========================

        high_val = chart_df["High"].max()
        low_val = chart_df["Low"].min()

        price_max = max(high_val,tp) * 1.08
        price_min = min(low_val,sl) * 0.95

        # =========================
        # STYLE
        # =========================

        style = mpf.make_mpf_style(
            base_mpf_style="nightclouds",
            facecolor="#0b1220",
            figcolor="#0b1220",
            gridcolor="#1f2937",
            gridstyle="--",
            y_on_right=True
        )

        # =========================
        # BUY & SELL PLOT
        # =========================
        buy_plot = mpf.make_addplot(
            buy_chart,
            type="scatter",
            marker="^",
            color=BUY_COLOR,
            markersize=120,
        )

        sell_plot = mpf.make_addplot(
            sell_chart,
            type="scatter",
            marker="v",
            color=SELL_COLOR,
            markersize=120,
        )

        if buy_chart.dropna().shape[0] > 0:
            apds.append(buy_plot)

        if sell_chart.dropna().shape[0] > 0:
            apds.append(sell_plot)


        # =========================
        # PLOT
        # =========================

        fig, axlist = mpf.plot(
            chart_df,
            type="candle",
            style=style,
            addplot=apds if len(apds)>0 else None,
            volume=True,
            volume_panel=1,
            volume_alpha=0.7,
            hlines=dict(
                hlines=[sl,tp],
                colors=[SL_COLOR,TP_COLOR],
                linewidths=1.5
            ),
            returnfig=True,
            figsize=(9,5),
            ylim=(price_min,price_max),
            fill_between=dict(
                y1=entry_low,
                y2=entry_high,
                alpha=0.07,
                color=ENTRY_ZONE_COLOR
            )
        )

        fig.text(
            0.5,
            0.97,
            f"{sym} | {trend} | {rs_label}",
            ha="center",
            fontsize=12,
            fontweight="bold",
            color="white"
        )

        fig.text(
            0.5,
            0.94,
            f"Entry {int(entry_low)}-{int(entry_high)}   SL {int(sl)}   TP {int(tp)}",
            ha="center",
            fontsize=10,
            color="white"
        )

        ax = axlist[0]
    
        ax.text(
            chart_df.index[-1],
            entry_high,
            " ENTRY",
            color="#fbbf24",
            fontsize=9
        )

        ax.text(
            0.02,
            0.92,
            f"Foreign: {ftxt}",
            transform=ax.transAxes,
            fontsize=9,
            bbox=dict(
                boxstyle="round",
                facecolor="#1f2937",
                alpha=0.8
            )
        )

        ax.text(
            chart_df.index[-1],
            tp,
            f" TP {int(tp)}",
            color="#00ff88",
            fontsize=9
        )

        ax.text(
            chart_df.index[-1],
            sl,
            f" SL {int(sl)}",
            color="#ff4d4d",
            fontsize=9
        )

        ax.text(
            0.02,
            0.88,
            f"{breakout_label}",
            transform=ax.transAxes,
            fontsize=10,
            fontweight="bold",
            color="white",
            ha="right",
            bbox=dict(
                boxstyle="round",
                facecolor="#16a34a" if breakout_label=="BREAKOUT" else "#f5930b",
                alpha=0.8
            )
        )

        ax.text(
            0.5,
            0.5,
            sym,
            transform=ax.transAxes,
            fontsize=38,
            color="white",
            alpha=0.03,
            ha="center",
            va="center",
            fontweight="bold"
        )

        ax.axhspan(
            zone_low,
            breakout,
            alpha=0.12,
            color=ACC_ZONE_COLOR
        )

        ax.axhspan(
            entry_low,
            entry_high,
            color=ENTRY_ZONE_COLOR,
            alpha=0.18
        )

        legend_items = [
            Line2D([0],[0],color=EMA9_COLOR,lw=2,label="EMA9"),
            Line2D([0],[0],color=EMA21_COLOR,lw=2,label="EMA21"),
            Line2D([0],[0],color=MA50_COLOR,lw=2,label="MA50"),
            Line2D([0],[0],color=VWAP_COLOR,lw=2,label="VWAP"),
            
            Line2D([0],[0],marker="^",color=BUY_COLOR,lw=0,label="BUY",markersize=10),
            Line2D([0],[0],marker="v",color=SELL_COLOR,lw=0,label="SELL",markersize=10),

            Line2D([0],[0],color=SL_COLOR,lw=2, label="STOP LOSS"),
            Line2D([0],[0],color=TP_COLOR,lw=2, label="TAKE PROFIT"),

            Patch(facecolor=ENTRY_ZONE_COLOR,alpha=0.18,edgecolor="none", label="ENTRY ZONE"),
            Patch(facecolor=ACC_ZONE_COLOR,alpha=0.12,edgecolor="none", label="ACCUMULATION ZONE")
        ]

        ax.legend(
            handles=legend_items,
            loc="center left",
            bbox_to_anchor=(-0.22, 0.5),
            fontsize=8,
            frameon=True,
            facecolor="#111827",
            edgecolor="gray",
            labelspacing=0.6,
            handlelength=1.6
        )

        fig.subplots_adjust(left=0.28, right=0.97, top=0.82, bottom=0.10)
        fig.savefig(file,dpi=120, facecolor=fig.get_facecolor(), pil_kwargs={"optimize": True, "compress_level": 9})

        if not os.path.exists(file):
            return None

        img = Image.open(file)
        img = img.convert("P", palette=Image.ADAPTIVE)

        img.save(
            file,
            format="PNG",
            optimize=True
        )

        plt.close('all')

        return file

    except Exception as e:

        print(f"Chart error {sym}: {e}")

        return None