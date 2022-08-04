import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from ProcessDocument import process_data

app = Flask(__name__)

filepath = None
params = {"x1": 0, "x2": 1000, "y1": 0, "y2": 1000, "t1": 0, "t2": 1000}
use_multiprocessing = False
plot_routes = False


@app.route('/')
def main():
    return render_template('main.html', filepath=filepath, params=params)


@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    global filepath
    if request.method == 'POST':
        f = request.files['json_file']
        fp = secure_filename(f.filename)
        filepath = os.path.abspath(fp)
    return render_template('upload_file.html', filepath=filepath)


@app.route('/set_params', methods=['GET', 'POST'])
def set_parameters():
    global params
    if request.method == 'POST':
        params.update({k: v for k, v in request.form.items() if k in ['x1', 'y1', 'x2', 'y2', 't1', 't2']})
    return render_template('set_params.html')


@app.route('/get_results', methods=['GET', 'POST'])
def get_results():
    global filepath, params, use_multiprocessing, plot_routes
    if request.method == 'POST':
        use_multiprocessing = 'multiprocessing' in request.form.keys() and request.form['multiprocessing'] == 'on'
        plot_routes = 'plot_routes' in request.form.keys() and request.form['plot_routes'] == 'on'
        doc = process_data(filepath, params, use_multiprocessing, plot_routes)
        with open(doc.result_path) as res_file:
            res = res_file.read()
        return render_template('get_results.html', result=res)


if __name__ == '__main__':
    app.run(debug=True)
