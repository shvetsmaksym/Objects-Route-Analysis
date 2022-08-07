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


def process_data(params, use_multiprocessing, filepath=None, document=None):
    p1 = (float(params['x1']), float(params['y1']))
    p2 = (float(params['x2']), float(params['y2']))
    time_range = (float(params['t1']), float(params['t2']))

    if document is None:
        clear_tmp()
        document = Document(filepath)

    document.split_input_json_data(use_multiprocessing=use_multiprocessing)
    document.set_criteria(time_range, p1, p2)
    document.update_jsons_and_get_results(use_multiprocessing=use_multiprocessing)

    return document


if __name__ == "__main__":
    if len(sys.argv) != 9:
        print('\nUsage: \n  python ProcessDocument.py -[MD] input x1 y1 x2 y2 t1 t2')
        print('\n Where: \n x1, y1, x2, y2 - two points corresponding to square area\n'
              't1, t2 - time range.')
        print('\nOptions:')
        print('\nM - multiprocessing mode')
    else:
        Filepath = sys.argv[2]
        Use_multiprocessing = 'M' in sys.argv[1]
        Params = {'x1': sys.argv[3], 'y1': sys.argv[4],
                  'x2': sys.argv[5], 'y2': sys.argv[6],
                  't1': sys.argv[7], 't2': sys.argv[8]
                  }  # (835, 940), (840, 950), (250, 350)

        doc = process_data(Params, Use_multiprocessing, filepath=Filepath)
        # doc.plot_routes()
