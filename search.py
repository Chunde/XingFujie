import sqlite3
from flask import Blueprint, request, session, render_template_string
from app import app

search_bp = Blueprint('search', __name__)

@search_bp.route('/search')
def search_page():
    # Retrieve accumulated results from the session
    accumulated_results = session.get('accumulated_results', [])
    columns = session.get('columns', [])

    # Generate the HTML table rows for accumulated results
    rows = ''.join(f'<tr>{"".join([f"<td>{field}</td>" for field in row])}</tr>' for row in accumulated_results)

    # Generate the table header with column names
    table_header = ''.join([f"<th>{col}</th>" for col in columns])

    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>数据库搜索</title>
        <!-- Include DataTables CSS -->
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
        <!-- Include jQuery -->
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
        <!-- Include DataTables JS -->
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    </head>
    <body>
        <h1>搜索数据库</h1>
        <form id="searchForm" action="/search_results" method="post">
            <input type="text" name="search_query" id="searchQuery" placeholder="输入搜索内容" value="{{ request.form['search_query'] if request.form.get('search_query') else '' }}">
            <button type="submit">搜索</button>
            <button type="button" id="clearResults">清除结果</button>
        </form>
        <br>
        <table id="resultsTable" class="display">
            <thead>
                <tr>{{ table_header | safe }}</tr>
            </thead>
            <tbody id="resultsBody">
                {{ rows | safe }}
            </tbody>
        </table>
        <script>
            $(document).ready(function() {
                $('#resultsTable').DataTable();
                $('#searchQuery').focus();
                $('#clearResults').click(function() {
                    $('#resultsBody').empty();
                    $('#searchQuery').val('').focus();
                });
            });
        </script>
    </body>
    </html>
    ''', rows=rows, table_header=table_header)

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

    # Retrieve accumulated results from the session and update with new results
    accumulated_results = session.get('accumulated_results', [])
    accumulated_results.extend(results)
    session['accumulated_results'] = accumulated_results
    session['columns'] = columns

    # Generate the HTML table rows for new search results
    rows = ''.join(f'<tr>{"".join([f"<td>{field}</td>" for field in row])}</tr>' for row in accumulated_results)

    # Generate the table header with column names
    table_header = ''.join([f"<th>{col}</th>" for col in columns])

    # Clear accumulated_results after displaying the results
    session['accumulated_results'] = []

    return render_template_string('''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>搜索结果</title>
        <!-- Include DataTables CSS -->
        <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.21/css/jquery.dataTables.min.css">
        <!-- Include jQuery -->
        <script type="text/javascript" charset="utf8" src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
        <!-- Include DataTables JS -->
        <script type="text/javascript" charset="utf8" src="https://cdn.datatables.net/1.10.21/js/jquery.dataTables.min.js"></script>
    </head>
    <body>
        <h1>搜索结果</h1>
        <form id="searchForm" action="/search_results" method="post">
            <input type="text" name="search_query" id="searchQuery" placeholder="输入搜索内容" value="{{ request.form['search_query'] if request.form.get('search_query') else '' }}">
            <button type="submit">搜索</button>
            <button type="button" id="clearResults">清除结果</button>
        </form>
        <br>
        <table id="resultsTable" class="display">
            <thead>
                <tr>{{ table_header | safe }}</tr>
            </thead>
            <tbody id="resultsBody">
                {{ rows | safe }}
            </tbody>
        </table>
        <script>
            $(document).ready(function() {
                $('#resultsTable').DataTable();
                $('#searchQuery').focus();
                $('#clearResults').click(function() {
                    $('#resultsBody').empty();
                    $('#searchQuery').val('').focus();
                });
            });
        </script>
    </body>
    </html>
    ''', rows=rows, table_header=table_header)
