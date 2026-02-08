import gc

def memory_guard(i):
    if i % 50 == 0:
        gc.collect()
