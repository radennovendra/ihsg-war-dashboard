import requests
from datetime import datetime
from config import TELEGRAM_TOKEN, CHAT_ID


def send(msg):
    if not TELEGRAM_TOKEN:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})


def format_net(net):

    if abs(net) >= 1e12:
        return f"{net/1e12:.2f}T"
    if abs(net) >= 1e9:
        return f"{net/1e9:.1f}B"
    if abs(net) >= 1e6:
        return f"{net/1e6:.1f}M"
    return str(int(net))


def send_daily_report(results, foreign_status=None):

    now = datetime.now().strftime("%d %b %Y")

    msg = f"📊 IHSG DAILY REPORT — {now}\n\n"

    # =========================
    # TOP WATCHLIST
    # =========================
    msg += "🔥 TOP WATCHLIST\n"

    for i, (sym, r) in enumerate(results[:5], 1):

        net = format_net(r.get("foreign_net", 0))

        msg += (
            f"\n{i}. {sym} | Score {r['score']}\n"
            f"Entry {r['entry_low']:.0f}-{r['entry_high']:.0f}\n"
            f"SL {r['stoploss']:.0f}\n"
            f"TP {r['tp2']:.0f}\n"
            f"Foreign {net} ({r.get('foreign_status')})\n"
        )

    # =========================
    # FOREIGN RANK
    # =========================
    msg += "\n🌍 TOP FOREIGN INFLOW\n"

    foreign_rank = sorted(
        results,
        key=lambda x: x[1].get("foreign_net", 0),
        reverse=True
    )

    for i, (sym, r) in enumerate(foreign_rank[:3], 1):
        msg += f"{i}. {sym} {format_net(r.get('foreign_net',0))}\n"

    # =========================
    # MARKET STATUS
    # =========================
    if foreign_status:
        msg += f"\n🧠 Market Flow: {foreign_status}\n"

    send(msg)