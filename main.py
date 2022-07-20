import os
import shutil
import json
from time import time

from logger import log
from DataStructures import *
from Constants import TMP_PATH


def clear_tmp():
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)

    if not os.path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)


if __name__ == "__main__":
    filepath = 'paths3.json'
    mp = False
    log(f"\n--- New document {filepath} --- \nMultiprocessing: {mp}")

    t1 = time()
    clear_tmp()
    t2 = time()
    log(f"Clear {TMP_PATH} directory in {round(t2-t1, 4)} seconds.")

    t1 = time()
    with open(filepath, 'r') as js_file:
        json_data = json.load(js_file)

    document = Document(filepath)
    document.split_input_json_data(json_data, multiprocessing=mp)
    t2 = time()
    log(f"Split input json file in {round(t2-t1, 4)} seconds.")

    p1, p2, time_range = (90, 400), (300, 405), (300, 950)
    document.set_criteria(time_range, p1, p2)

    t1 = time()
    document.update_routes_with_entries_exists_info(multiprocessing=mp)
    t2 = time()
    log(f"Update routes with entries and exists information in {round(t2-t1, 4)} seconds.")

    t1 = time()
    document.get_results(multiprocessing=mp)
    t2 = time()
    log(f"Write all routes' entries and exits into results.txt in {round(t2-t1, 4)} seconds.")

    t1 = time()
    document.plot_routes(multiprocessing=mp)
    t2 = time()
    log(f"Plot routes in {round(t2 - t1, 4)} seconds.")




