# main.py
from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import sqlite3
import os
import csv

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Define database file path
DATABASE = 'attendance.db'
ADMIN_PASSWORD = 'admin123'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        police_station TEXT,
                        police_id TEXT,
                        rank TEXT,
                        duty_date TEXT,
                        latitude REAL,
                        longitude REAL,
                        timestamp TEXT
                    )''')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    police_station = request.form['police_station']
    police_id = request.form['police_id']
    rank = request.form['rank']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    duty_date = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO attendance (name, police_station, police_id, rank, duty_date, latitude, longitude, timestamp)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (name, police_station, police_id, rank, duty_date, latitude, longitude, timestamp))

    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin.html', error='Incorrect password')
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    name_filter = request.args.get('name', '')
    date_filter = request.args.get('date', '')

    query = 'SELECT * FROM attendance WHERE 1=1'
    params = []
    if name_filter:
        query += ' AND name LIKE ?'
        params.append(f"%{name_filter}%")
    if date_filter:
        query += ' AND duty_date = ?'
        params.append(date_filter)

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()

    return render_template('dashboard.html', records=rows)

@app.route('/download')
def download():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM attendance')
        rows = c.fetchall()

    filepath = 'attendance.csv'
    with open(filepath, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Police Station', 'Police ID', 'Rank', 'Duty Date', 'Latitude', 'Longitude', 'Timestamp'])
        writer.writerows(rows)

    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    init_db()
    import os

    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)