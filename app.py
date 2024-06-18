from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2
from concurrent.futures import ThreadPoolExecutor
import os

app = Flask(__name__)

# Configure your PostgreSQL connection
DB_CONFIG = {
    'dbname': 'risk_modeler_dev',
    'user': 'postgres',
    'password': 'U[<3jrPz6>8#',
    'host': '34.194.238.112',
    'port': '5678'
}

executor = ThreadPoolExecutor(max_workers=5)

def run_query(query):
    try:
        with psycopg2.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                if cur.description:
                    # Fetch results if it's a SELECT query
                    result = cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return {"status": "success", "data": {"columns": columns, "rows": result}}
                else:
                    # Commit the transaction if it's not a SELECT query
                    conn.commit()
                    return {"status": "success", "message": "Query executed successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def execute_sql_file(filename):
    with open(filename, 'r') as file:
        query = file.read()
    return run_query(query)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def execute_query():
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({"status": "error", "message": "No query provided"}), 400

    future = executor.submit(run_query, query)
    future.add_done_callback(lambda f: print(f.result()))
    
    result = future.result()
    return jsonify(result)

@app.route('/dashboard')
def dashboard():
    return render_template('query.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    if username == 'admin' and password == 'admin':
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('index', error='Invalid credentials'))

if __name__ == '__main__':
    app.run(debug=True)
