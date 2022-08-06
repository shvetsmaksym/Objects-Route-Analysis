import os
import json
import csv
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from DataStructures import Document
from ProcessDocument import clear_tmp, process_data

app = Flask(__name__)

filepath = None
params = {"x1": 0, "x2": 1000, "y1": 0, "y2": 1000, "t1": 0, "t2": 1000}
use_multiprocessing = False
document = None


@app.route('/')
def main():
    filename = os.path.basename(filepath) if filepath else None
    return render_template('main.html', filepath=filename, params=params)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global filepath
    if request.method == 'POST':
        f = request.files['json_file']
        fp = secure_filename(f.filename)
        filepath = os.path.abspath(fp)
    return render_template('upload_file.html', filepath=filepath)


@app.route('/list_routes', methods=['GET', 'POST'])
def list_routes():
    global document, filepath, use_multiprocessing

    if document is None or document.filepath != filepath:
        clear_tmp()
        with open(filepath, 'r') as js_file:
            json_data = json.load(js_file)
        document = Document(filepath)
        document.split_input_json_data(json_data, multiprocessing=use_multiprocessing)

    with open(document.map_jsons_path, 'r') as csv_file:
        map_files = list(csv.reader(csv_file, delimiter=";"))

    return render_template('list_routes.html', result=map_files)


@app.route('/set_params', methods=['GET', 'POST'])
def set_parameters():
    global params, use_multiprocessing
    if request.method == 'POST':
        params.update({k: v for k, v in request.form.items() if k in ['x1', 'y1', 'x2', 'y2', 't1', 't2']})
        use_multiprocessing = 'multiprocessing' in request.form.keys() and request.form['multiprocessing'] == 'on'
    return render_template('set_params.html', x1=params['x1'], y1=params['y1'],
                           x2=params['x2'], y2=params['y2'],
                           t1=params['t1'], t2=params['t2'])


@app.route('/get_results', methods=['GET', 'POST'])
def get_results():
    global document, filepath, params, use_multiprocessing
    if request.method == 'POST':
        if document is None or document.filepath != filepath:
            document = process_data(params, use_multiprocessing, filepath=filepath)
        else:
            document = process_data(params, use_multiprocessing, document=document)

        with open(document.result_path, 'r') as res_file:
            res = res_file.read()
        return render_template('get_results.html', result=res)


if __name__ == '__main__':
    app.run(debug=True)
