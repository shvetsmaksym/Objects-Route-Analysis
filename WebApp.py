import json
import os
import shutil
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from logger import log, timer_func
from DataStructures import *
from Constants import TMP_PATH

app = Flask(__name__)

filepath = ""
params = {}
use_multiprocessing = False
plot_routes = False


@app.route('/')
def main():
    return render_template('main_template.html', filepath=filepath, params=params)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global filepath, params
    if request.method == 'POST':
        f = request.files['json_file']
        fp = secure_filename(f.filename)
        filepath = os.path.abspath(fp)
    return render_template('main_template.html', filepath=filepath, params=params)


@app.route('/set_params', methods=['GET', 'POST'])
def set_parameters():
    return render_template('set_params_template.html')


@app.route('/with_set_params', methods=['GET', 'POST'])
def with_set_params():
    global filepath, params
    if request.method == 'POST':
        params = {k: v for k, v in request.form.items() if k in ['x1', 'y1', 'x2', 'y2', 't1', 't2']}
        return render_template('main_template.html', filepath=filepath, params=params)


@app.route('/get_results', methods=['GET', 'POST'])
def get_results():
    global use_multiprocessing, plot_routes
    if request.method == 'POST':
        use_multiprocessing = 'multiprocessing' in request.form.keys() and request.form['multiprocessing'] == 'on'
        plot_routes = 'plot_routes' in request.form.keys() and request.form['plot_routes'] == 'on'
        doc = process_data()
        with open(doc.result_path) as res_file:
            res = res_file.read()
        return render_template('get_results.html', result=res)


@timer_func
def clear_tmp():
    if os.path.exists(TMP_PATH):
        shutil.rmtree(TMP_PATH)

    if not os.path.exists(TMP_PATH):
        os.mkdir(TMP_PATH)


def process_data():
    global filepath, params, use_multiprocessing, plot_routes
    p1 = (float(params['x1']), float(params['y1']))
    p2 = (float(params['x2']), float(params['y2']))
    time_range = (float(params['t1']), float(params['t2']))
    log(f"--- New document {filepath} --- \nMultiprocessing: {use_multiprocessing}")
    clear_tmp()

    with open(filepath, 'r') as js_file:
        json_data = json.load(js_file)

    document = Document(filepath)
    document.split_input_json_data(json_data, multiprocessing=use_multiprocessing)
    document.set_criteria(time_range, p1, p2)
    document.update_routes_with_entries_exists_info(multiprocessing=use_multiprocessing)
    document.get_results(multiprocessing=use_multiprocessing)

    if plot_routes:
        document.plot_routes()

    return document


if __name__ == '__main__':
    app.run(debug=True)
