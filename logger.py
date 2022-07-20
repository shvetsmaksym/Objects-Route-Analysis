from datetime import datetime
import os

LOG_DIR = 'logs'
LOG_PATH = log_path = os.path.join(LOG_DIR, f"{datetime.now().year}_{datetime.now().month}_{datetime.now().day}.log")


def log(log_to_write):
    print(log_to_write)
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

    with open(LOG_PATH, 'a') as f:
        f.write(f"[{datetime.now().hour}:{datetime.now().minute}:{datetime.now().second}]\t" + str(log_to_write) + '\n')
