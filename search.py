# search.py
import sqlite3
from flask import Blueprint, request, render_template_string
from app import app  # Assuming 'app' is defined in app.py

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search_page():
    return '''
    <!doctype html>
    <title>数据库搜索</title>
    <h1>搜索数据库</h1>
    <form action="/search_results" method="post">
      <input type="text" name="search_query" placeholder="输入搜索内容">
      <button type="submit">搜索</button>
    </form>
    <br>
    <table id="resultsTable">
      <thead>
        <tr>
          <th>ID</th>
          <th>列1</th>
          <th>列2</th>
          <th>列3</th>
          <!-- Add more column headers as needed -->
        </tr>
      </thead>
      <tbody id="resultsBody">
      </tbody>
    </table>
    '''

@search_bp.route('/search_results', methods=['POST'])
def search_results():
    search_query = request.form['search_query']
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()

    # Dynamically fetch the column names
    c.execute("PRAGMA table_info(processed_data)")
    columns = [info[1] for info in c.fetchall()]

    # Construct the search query
    query = f"SELECT * FROM processed_data WHERE {' OR '.join([f'{col} LIKE ?' for col in columns])}"
    params = [f'%{search_query}%'] * len(columns)

    c.execute(query, params)
    results = c.fetchall()
    conn.close()

    # Generate the HTML table rows
    rows = ''.join(f'<tr>{" ".join([f"<td>{field}</td>" for field in row])}</tr>' for row in results)

    return render_template_string(f'''
    <!doctype html>
    <title>搜索结果</title>
    <h1>搜索结果</h1>
    <a href="/search">返回搜索</a>
    <br><br>
    <table id="resultsTable">
      <thead>
        <tr>{" ".join([f"<th>{col}</th>" for col in ["ID"] + columns])}</tr>
      </thead>
      <tbody id="resultsBody">
        {rows}
      </tbody>
    </table>
    ''')

