import sqlite3
import os
import json

# Get path to the database file
db_path = os.path.join(os.path.dirname(__file__), "api_data.db")
print("Database path:", db_path)

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Retrieve all records from the table
cursor.execute("SELECT * FROM aircraft_data")
rows = cursor.fetchall()

# Define expected field labels to display
field_labels = [
    "PILOT", "AMA#", "FAA#", "PH#", "BUILDER", 
    "MODEL", "SERIAL NO.", "PROD. CERT.", "TYPE CERT."
]

def parse_qr_data(qr_string):
    """
    Parse QR data string into a dictionary.
    Supports JSON format and key:value;key:value format.
    """
    try:
        # Try parsing as JSON
        return json.loads(qr_string)
    except json.JSONDecodeError:
        # Fallback: try parsing as key:value;key:value
        parsed_data = {}
        pairs = qr_string.split(';')
        for pair in pairs:
            if ':' in pair:
                key, value = pair.split(':', 1)
                parsed_data[key.strip()] = value.strip()
        return parsed_data

# Display results
if rows:
    print("\n--- Stored Aircraft Data ---\n")
    for idx, row in enumerate(rows, start=1):
        record_id, qr_data = row
        print(f"Record {idx} - ID: {record_id}")
        parsed_fields = parse_qr_data(qr_data)
        for label in field_labels:
            print(f"{label:<12}: {parsed_fields.get(label, 'N/A')}")
        print("-" * 40)
else:
    print("No data found in the database.")

# Close database connection
conn.close()
