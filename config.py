TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
SCORE_VERSION = "v4"

# ==========================
# MODE SWITCH
# ==========================
MODE = "AGGRESSIVE"
# MODE = "ULTRA"

# ==========================
# WATCHLIST MODE
# ==========================
WATCHLIST_MODE = True
WATCHLIST_TOPN = 10

# ==========================
# MODE PARAMETERS
# ==========================
if MODE == "ULTRA":
    MIN_SCORE = 70
    MIN_AVG_VALUE = 100_000_000_000
    DISCOUNT_LEVEL = -0.40
else:  # AGGRESSIVE
    MIN_SCORE = 50
    MIN_AVG_VALUE = 10_000_000_000
    DISCOUNT_LEVEL = -0.20


# ==========================
# SYSTEM LIMITS
# ==========================
MAX_ALERTS = 5
BATCH_LIMIT = 200   # keep safe (avoid yfinance crash)
