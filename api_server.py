from flask import Flask, request, jsonify
import sqlite3
import os
import json

app = Flask(__name__)
DB_NAME = 'api_data.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DB_NAME)
    print("Database path:", os.path.abspath(DB_NAME))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS aircraft_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qr_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Endpoint to receive QR data
@app.route('/store_data', methods=['POST'])
def store_data():
    data = request.get_json()

    if not data or 'qr_data' not in data:
        return jsonify({'error': 'Invalid request, missing qr_data'}), 400

    qr_data_raw = data['qr_data']

    if not isinstance(qr_data_raw, dict):
        return jsonify({'error': 'qr_data must be a JSON object/dictionary'}), 400

    try:
        qr_data_str = json.dumps(qr_data_raw)  # Convert dict to JSON string for DB
    except Exception as e:
        return jsonify({'error': 'Error encoding qr_data to JSON', 'details': str(e)}), 400

    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO aircraft_data (qr_data) VALUES (?)", (qr_data_str,))
        conn.commit()
        conn.close()
    except Exception as e:
        return jsonify({'error': 'Database error', 'details': str(e)}), 500

    print("\n--- QR Data Extracted ---")
    for key, value in qr_data_raw.items():
        print(f'{key}: "{value}"')

    return jsonify({'message': 'Data stored and printed successfully'}), 200

# ✅ Separate endpoint to view stored data in browser
@app.route('/view_data', methods=['GET'])
def view_data():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('SELECT * FROM aircraft_data')
    rows = c.fetchall()
    conn.close()

    # Optional: parse back JSON strings
    parsed_rows = []
    for row in rows:
        try:
            parsed_json = json.loads(row[1])
        except:
            parsed_json = row[1]
        parsed_rows.append({'id': row[0], 'qr_data': parsed_json})

    return jsonify(parsed_rows)

# Run the server
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
