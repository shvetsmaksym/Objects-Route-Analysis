from datetime import datetime
import os
from time import time
from Constants import LOG_DIR

LOG_PATH = log_path = os.path.join(LOG_DIR, f"{datetime.now().year}_{datetime.now().month}_{datetime.now().day}.log")


def log(log_to_write):
    print(log_to_write)
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    with open(LOG_PATH, 'a') as f:
        f.write(f"[{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}]\t" + str(log_to_write) + '\n')


def timer_func(func):
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        if t2 - t1 > 1e-5:
            if 'use_multiprocessing' in kwargs.keys():
                log(f"Function {func.__name__!r} executed in {(t2-t1):.4f} seconds; "
                    f"multiprocessing: {kwargs['use_multiprocessing']}")
            else:
                log(f"Function {func.__name__!r} executed in {(t2 - t1):.4f} seconds.")
        return result
    return wrap_func
