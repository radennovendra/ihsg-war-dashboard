import requests
from datetime import datetime

from config import TELEGRAM_TOKEN, CHAT_ID


# =========================
# SEND
# =========================
def send(msg):

    if not TELEGRAM_TOKEN:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    try:
        requests.post(url, data={
            "chat_id": CHAT_ID,
            "text": msg
        }, timeout=10)
    except:
        pass


# =========================
# FORMAT
# =========================
def fmt(net):

    if abs(net) >= 1e12:
        return f"{net/1e12:.2f}T"
    if abs(net) >= 1e9:
        return f"{net/1e9:.1f}B"
    if abs(net) >= 1e6:
        return f"{net/1e6:.1f}M"
    return str(int(net))


# =========================
# MORNING REPORT
# =========================
def morning_report(results, foreign_status):

    msg = "🌅 MORNING FLOW REPORT\n\n"

    msg += f"Market Flow: {foreign_status}\n\n"

    msg += "🔥 Watchlist Focus:\n"

    for sym, r in results[:5]:

        msg += (
            f"\n{sym}\n"
            f"Entry {r['entry_low']:.0f}-{r['entry_high']:.0f}\n"
            f"SL {r['stoploss']:.0f}\n"
            f"Foreign {fmt(r.get('foreign_net',0))}\n"
        )

    send(msg)


# =========================
# INTRADAY ALERT
# =========================
def intraday_alert(sym, r):

    msg = (
        f"🚨 INTRADAY SIGNAL\n"
        f"{sym}\n\n"
        f"Score {r['score']}\n"
        f"Entry {r['entry_low']:.0f}-{r['entry_high']:.0f}\n"
        f"SL {r['stoploss']:.0f}\n"
        f"TP {r['tp2']:.0f}\n"
        f"Foreign {fmt(r.get('foreign_net',0))}"
    )

    send(msg)


# =========================
# DAILY HEDGE FUND REPORT
# =========================
def daily_report(results, foreign_status):

    today = datetime.now().strftime("%d %b")

    msg = f"📊 HEDGE FUND REPORT {today}\n\n"

    msg += f"Market Flow: {foreign_status}\n\n"

    msg += "🏆 Top Watchlist\n"

    for i, (sym, r) in enumerate(results[:5], 1):

        msg += (
            f"\n{i}. {sym} ({r['score']})\n"
            f"Entry {r['entry_low']:.0f}-{r['entry_high']:.0f}\n"
            f"TP {r['tp2']:.0f}\n"
            f"Foreign {fmt(r.get('foreign_net',0))}\n"
        )

    msg += "\n🌍 Top Foreign Inflow\n"

    foreign_rank = sorted(
        results,
        key=lambda x: x[1].get("foreign_net", 0),
        reverse=True
    )

    for i, (sym, r) in enumerate(foreign_rank[:3], 1):
        msg += f"{i}. {sym} {fmt(r.get('foreign_net',0))}\n"

    send(msg)