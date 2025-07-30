import sqlite3

# Connect to (or create) the database
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create the attendance table
cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    officer_name TEXT NOT NULL,
    rank TEXT NOT NULL,
    police_station TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    latitude TEXT,
    longitude TEXT
)
''')

conn.commit()
conn.close()
print("✅ Database created successfully: attendance.db")