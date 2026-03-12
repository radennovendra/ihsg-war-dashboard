def tick_size(price):

    if price < 200:
        return 1
    elif price < 500:
        return 2
    elif price < 2000:
        return 5
    elif price < 5000:
        return 10
    else:
        return 25


def round_tick(price):

    tick = tick_size(price)
    return round(price / tick) * tick


def floor_tick(price):

    tick = tick_size(price)
    return int(price / tick) * tick


def ceil_tick(price):

    tick = tick_size(price)
    return (int(price / tick) + 1) * tick