import os
import csv
from PIL import Image
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from DataStructures import Document
from ProcessDocument import clear_tmp, process_data
from Constants import PLOT_PATH_STATIC
from logger import log

app = Flask(__name__)

filepath = None
params = {"x1": 0, "x2": 1000, "y1": 0, "y2": 1000, "t1": 0, "t2": 1000}
use_multiprocessing = False
document = None


@app.route('/')
def main():
    global filepath, params, use_multiprocessing
    filename = os.path.basename(filepath) if filepath else None
    return render_template('main.html', filepath=filename, params=params, proc=use_multiprocessing)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global filepath
    f_name = None
    if request.method == 'POST':
        f = request.files['json_file']
        fp = secure_filename(f.filename)
        filepath = os.path.abspath(fp)
        f_name = os.path.basename(filepath)
    return render_template('upload_file.html', f_name=f_name)


@app.route('/list_routes', methods=['GET', 'POST'])
def list_routes():
    global document, filepath, use_multiprocessing
    if filepath is None:
        return render_template('list_routes.html', result=[["No json file chosen."]])
    if document is None or document.filepath != filepath:
        clear_tmp()
        document = Document(filepath)
        create_empty_img()

        # At this stage we assume, that user may not set parameter 'use multiprocessing' yet.
        # Therefore, the program decides whether to use multiprocessing or not based on the size of input file.
        proc = os.path.getsize(filepath) > 1e7 or use_multiprocessing
        document.split_input_json_data(use_multiprocessing=proc)

    with open(document.map_jsons_path, 'r') as csv_file:
        map_files = list(csv.reader(csv_file, delimiter=";"))

    if request.method == 'POST':
        routes_list = [k for k, v in request.form.items() if k.endswith(".json") and v == "on"]
        document.plot_routes(routes_list=routes_list, to_static_dir=True)
        return render_template('list_routes.html', result=map_files, routes_img_src=PLOT_PATH_STATIC)

    return render_template('list_routes.html', result=map_files, routes_img_src="None")


@app.route('/set_params', methods=['GET', 'POST'])
def set_parameters():
    global params, use_multiprocessing
    if request.method == 'POST':
        params.update({k: v for k, v in request.form.items() if k in ['x1', 'y1', 'x2', 'y2', 't1', 't2']})
        use_multiprocessing = 'multiprocessing' in request.form.keys() and request.form['multiprocessing'] == 'on'
        log(f"Multiprocessing mode was changed to: {use_multiprocessing}")
    return render_template('set_params.html', x1=params['x1'], y1=params['y1'],
                           x2=params['x2'], y2=params['y2'],
                           t1=params['t1'], t2=params['t2'],
                           proc=use_multiprocessing)


@app.route('/get_results', methods=['GET', 'POST'])
def get_results():
    global document, filepath, params, use_multiprocessing

    if filepath is None:
        return render_template('get_results.html', result=[["No json file chosen."]])
    if request.method == 'POST':
        if document is None or document.filepath != filepath:
            document = process_data(params, use_multiprocessing, filepath=filepath)
            create_empty_img()
        else:
            document = process_data(params, use_multiprocessing, document=document)

        with open(document.result_path, 'r') as txt_file:
            res = list(csv.reader(txt_file, delimiter=";"))
        return render_template('get_results.html', result=res)


def create_empty_img():
    img = Image.new(mode='RGB', size=(640, 480), color=(255, 255, 255))
    img.save(PLOT_PATH_STATIC)
    img.close()


if __name__ == '__main__':
    create_empty_img()  # css/routes.png

    app.run(debug=True)

    if os.path.exists(PLOT_PATH_STATIC):
        os.remove(PLOT_PATH_STATIC)
