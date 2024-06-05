#!/usr/bin/python3
import os
import re
from flask import Flask, request, send_file, redirect, url_for
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
from convert_tmall import *
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>幸福街表格转换</title>
    <h1>请上传要处理的文件</h1>
    <form id="uploadForm" method=post enctype=multipart/form-data action="/upload">
      <input type=file name=file id="fileInput" style="display:none;" onchange="document.getElementById('uploadForm').submit();">
      <button type="button" onclick="document.getElementById('fileInput').click();">打开上传</button>
    </form>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(url_for('index'))
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        processed_path = tmall_process_excel_file(input_path)
        return send_file(processed_path, as_attachment=True)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8080)