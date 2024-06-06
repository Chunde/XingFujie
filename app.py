from flask import Flask, request, send_file, redirect, url_for, render_template, session, Blueprint
import os
import sqlite3
from flask import Flask, request, send_file, redirect, url_for
import pandas as pd
import sqlite3
from datetime import datetime
from werkzeug.utils import secure_filename
from convert_tmall import tmall_process_excel_file  # Ensure this function is defined in convert_tmall module

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'xls', 'xlsx'}
app.config['DATABASE'] = 'database.db'
app.secret_key = 'supersecretkey'  # Add a secret key for session management

# Ensure upload and processed directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def init_db(columns):
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Create table with dynamic columns
    columns_sql = ', '.join([f'"{col}" TEXT' for col in columns])
    create_table_sql = f'''
    CREATE TABLE IF NOT EXISTS processed_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        {columns_sql}
    )
    '''
    c.execute(create_table_sql)
    conn.commit()
    conn.close()

def insert_data_into_db(dataframe):
    conn = sqlite3.connect(app.config['DATABASE'])
    dataframe.to_sql('processed_data', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()

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
    <br>
    <form action="/search">
      <button type="submit">搜索数据库</button>
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

        # Load the processed file into a pandas DataFrame
        processed_df = pd.read_excel(processed_path)
        
        # Check if database exists, and initialize it with columns if not
        if not os.path.exists(app.config['DATABASE']):
            init_db(processed_df.columns)

        # Insert data into the database
        insert_data_into_db(processed_df)

        return send_file(processed_path, as_attachment=True)
    else:
        return redirect(url_for('index'))

@app.errorhandler(Exception)
def handle_exception(e):
    return render_template("error.html", error_message=str(e)), 500

if __name__ == '__main__':
    from search import search_bp  # Import the search blueprint

    app.register_blueprint(search_bp)  # Register the search blueprint
    
    app.run(host='0.0.0.0', port=8080)
