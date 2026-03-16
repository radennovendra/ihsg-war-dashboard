from scanner import run
from twitter_engine import tweet_chart
from twitter_signal import build_tweet
from utils.chart_generator import generate_chart

signals = run()

for s in signals[:0]:

    sym = s["symbol"]

    tweet = build_tweet(sym, s)

    chart = generate_chart(sym, s)

    if chart:
        tweet_chart(chart, tweet)