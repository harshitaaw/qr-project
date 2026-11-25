import sqlite3

conn = sqlite3.connect("api_data.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS qr_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qr_content TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database and table created successfully.")
