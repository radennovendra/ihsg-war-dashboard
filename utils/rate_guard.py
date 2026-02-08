import time

LAST_CALL = 0

def guard(min_delay=0.2):
    global LAST_CALL

    now = time.time()
    diff = now - LAST_CALL

    if diff < min_delay:
        time.sleep(min_delay - diff)

    LAST_CALL = time.time()
