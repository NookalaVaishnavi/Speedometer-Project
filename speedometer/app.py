from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import random
import time
from threading import Thread

app = Flask(__name__)
CORS(app)

# Database initialization
DB_NAME = "speed_data.db"
inserting_data = False 

def init_db():
    print("Initializing the database...")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS speed_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            speed REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
    print("Database initialized.")

def insert_data():
    """Insert random data into the database every second when flag is True"""
    global inserting_data
    while inserting_data:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        speed = random.randint(1, 100)
        cursor.execute("INSERT INTO speed_data (timestamp, speed) VALUES (?, ?)", (timestamp, speed))
        conn.commit()
        conn.close()
        print(f"Inserted: {timestamp}, {speed}")
        time.sleep(1)

@app.route('/api/speed', methods=['GET'])
def get_speed():
    """API endpoint to fetch the latest speed data"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, speed FROM speed_data ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return jsonify({"timestamp": row[0], "speed": row[1]})
    else:
        return jsonify({"error": "No data available"}), 404

@app.route('/api/start', methods=['POST'])
def start_insertion():
    """Start inserting data into the database"""
    global inserting_data
    if not inserting_data:
        inserting_data = True
        thread = Thread(target=insert_data, daemon=True)
        thread.start()
        return jsonify({"message": "Data insertion started."})
    else:
        return jsonify({"message": "Data insertion is already running."})

@app.route('/api/stop', methods=['POST'])
def stop_insertion():
    """Stop inserting data into the database"""
    global inserting_data
    if inserting_data:
        inserting_data = False
        return jsonify({"message": "Data insertion stopped."})
    else:
        return jsonify({"message": "Data insertion is not running."})

if __name__ == "__main__":
    init_db()  # Initialize the database
    app.run(debug=True)
