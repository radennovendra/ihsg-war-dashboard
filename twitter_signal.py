def build_tweet(sym, r):

    entry = f"{int(r['entry_low'])}-{int(r['entry_high'])}"

    tweet = f"""
📊 IHSG Smart Money Signal

{sym}

Score : {r['score']}
Entry : {entry}
TP : {int(r['tp2'])}
SL : {int(r['stoploss'])}

#IHSG #{sym.replace('.JK','')}
"""

    return tweet