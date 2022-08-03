import os
import shutil
import json
import sys

from logger import log, timer_func
from DataStructures import *
from Constants import TMP_PATH


@timer_func
def clear_tmp():
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)

    if not os.path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)


if __name__ == "__main__":
    if len(sys.argv) < 8 or len(sys.argv) > 9:
        print('\nUsage: \n  python main.py -[MD] input x1 y1 x2 y2 t1 t2')
        print('\n Where: \n x1, y1, x2, y2 - two points corresponding to square area\n'
              't1, t2 - time range.')
        print('\nOptions:')
        print('\nM - multiprocessing mode')
        print('\nD - plot routes and save them as image file.')
    else:
        filepath = sys.argv[2]
        plot_r = 'D' in sys.argv[1]
        mp = 'M' in sys.argv[1]
        p1, p2, time_range = (float(sys.argv[3]), float(sys.argv[4])), (float(sys.argv[5]), float(sys.argv[6])),\
                             (float(sys.argv[7]), float(sys.argv[8]))  # (835, 940), (840, 950), (250, 350)
        log(f"--- New document {filepath} --- \nMultiprocessing: {mp}")

        clear_tmp()

        with open(filepath, 'r') as js_file:
            json_data = json.load(js_file)

        document = Document(filepath)
        document.split_input_json_data(json_data, multiprocessing=mp)
        document.set_criteria(time_range, p1, p2)
        document.update_routes_with_entries_exists_info(multiprocessing=mp)
        document.get_results(multiprocessing=mp)

        if plot_r:
            document.plot_routes()

