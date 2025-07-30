from flask import Flask, render_template, request, redirect, url_for, session, send_file
from datetime import datetime
import sqlite3
import csv
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DATABASE = 'attendance.db'

# --- Setup database ---
def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        police_id TEXT NOT NULL,
        rank TEXT NOT NULL,
        station TEXT NOT NULL,
        latitude TEXT,
        longitude TEXT,
        duty_date TEXT,
        timestamp TEXT
    )''')
    conn.commit()
    conn.close()

# --- Home Page ---
@app.route('/')
def index():
    ranks = ["DySP", "IoP", "SI", "ASI", "GSI", "GASI", "SCPO", "GSCPO", "CPO", "WSCPO", "WCPO", "AC", "RSI", "RASI", "MTSI", "GRSI", "GRASI", "Armr SI", "Armr GASI", "Armr SCPO", "Armr CPO", "KHG", "RTPC", "CF"]
    stations = [
        "TOWN SOUTH", "CONTROL ROOM", "TRAFFIC PALAKKAD", "TOWN NORTH", "MANKARA", "KASABA", "WALAYAR",
        "HEMAMBIKA NAGAR", "MALAMPUZHA", "CHITTUR", "MEENAKSHIPURAM", "KOZHINJAMPARA", "KOLLENGODE",
        "PUDUNAGARAM", "PARAMBIKULAM", "ALATHUR", "KOTTAYI", "KUZHALMANNAM", "VADAKKENCHERRY",
        "MANGALAMDAM", "NEMMARA", "PADAGIRI", "OTTAPALAM", "OTTAPALAM TRAFFIC", "SHORNUR", "PATTAMBI",
        "PATTAMBI TRAFFIC", "KOPPAM", "THRITHALA", "CHALISSERY", "CHERPULASSERY", "SREEKRISHNAPURAM",
        "MANNARKKAD", "NATTUKAL", "KONGAD", "MANNARKKAD TRAFFIC", "KALLADIKKODE", "SMS AGALI", "AGALI",
        "SHOLAYUR", "PUDUR", "SPECIAL BRANCH", "DCRB", "DCB", "CYBER CELL", "CYBER CRIME",
        "NARCOTIC CELL", "WOMEN CELL", "VANITHA", "TOURISM POLICE", "DCPHQ", "DHQ"
    ]
    return render_template('index.html', ranks=ranks, stations=stations)

# --- Handle form ---
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    police_id = request.form['police_id']
    rank = request.form['rank']
    station = request.form['station']
    latitude = request.form['latitude']
    longitude = request.form['longitude']
    duty_date = datetime.now().strftime('%Y-%m-%d')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''INSERT INTO attendance (name, police_id, rank, station, latitude, longitude, duty_date, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (name, police_id, rank, station, latitude, longitude, duty_date, timestamp))
    conn.commit()
    conn.close()
    return redirect('/')

# --- Admin login ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form['password'] == 'admin123':
            session['admin'] = True
            return redirect('/dashboard')
    return render_template('admin.html')

# --- Dashboard ---
@app.route('/dashboard')
def dashboard():
    if not session.get('admin'):
        return redirect('/admin')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('dashboard.html', records=rows)

# --- Download CSV ---
@app.route('/download')
def download():
    if not session.get('admin'):
        return redirect('/admin')
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance")
    rows = c.fetchall()
    conn.close()

    filename = 'attendance_data.csv'
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Police ID', 'Rank', 'Station', 'Latitude', 'Longitude', 'Duty Date', 'Timestamp'])
        writer.writerows(rows)
    return send_file(filename, as_attachment=True)

# --- Logout ---
@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)
