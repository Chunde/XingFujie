import os
import re
from flask import Flask, request, send_file, redirect, url_for
import pandas as pd
from datetime import datetime
from werkzeug.utils import secure_filename
from convert_douyin import *
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# def clean_property(prop):
#     cleaned_prop = re.sub(r'\(.*?\)', '', prop)
#     return cleaned_prop.strip()

# def split_property(prop):
#     category_pattern = r'^[A-Za-z0-9]+(?=[\u4e00-\u9fff])'
#     color_pattern = r'[\u4e00-\u9fff].*?(?=;)'
#     size_pattern = r'(?<=:)\d+'

#     category_match = re.search(category_pattern, prop)
#     category = category_match.group() if category_match else None

#     if category:
#         color_match = re.search(color_pattern, prop[len(category):])
#         color = color_match.group().strip() if color_match else None
#     else:
#         color = None

#     if color:
#         size_match = re.search(size_pattern, prop[prop.find(color) + len(color):])
#         size = size_match.group() if size_match else None
#     else:
#         size = None

#     return [category, size, color]

# def process_excel_file(input_path):
#     file_extension = input_path.split('.')[-1]

#     if file_extension == 'xls':
#         df = pd.read_excel(input_path, sheet_name=0, engine='xlrd')
#     elif file_extension == 'xlsx':
#         df = pd.read_excel(input_path, sheet_name=0, engine='openpyxl')
#     else:
#         raise ValueError("Unsupported file format. Please provide an Excel file with .xls or .xlsx extension.")

#     df['cleaned_property'] = df['property'].apply(clean_property)
#     df[['category', 'size', 'color']] = df['cleaned_property'].apply(lambda x: pd.Series(split_property(x)))
#     df.drop(columns=['cleaned_property'], inplace=True)
#     df = df.dropna(subset=['color'])

#     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#     output_filename = f"processed_{timestamp}.xlsx"
#     output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)
#     df.to_excel(output_path, index=False, engine='openpyxl')

#     return output_path

@app.route('/')
def index():
    return '''
    <!doctype html>
    <title>Upload Excel File</title>
    <h1>Upload Excel File for Processing</h1>
    <form id="uploadForm" method=post enctype=multipart/form-data action="/upload">
      <input type=file name=file id="fileInput" style="display:none;" onchange="document.getElementById('uploadForm').submit();">
      <button type="button" onclick="document.getElementById('fileInput').click();">Upload File</button>
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
        processed_path = process_excel_file(input_path)
        return send_file(processed_path, as_attachment=True)
    else:
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
