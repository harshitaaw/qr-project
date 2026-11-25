import cv2
from pyzbar.pyzbar import decode, ZBarSymbol
import tkinter as tk
from tkinter import messagebox, filedialog
import sqlite3
import csv
import requests
import os
import time

# -------------------- Database Setup --------------------
def setup_database():
    conn = sqlite3.connect('aircraft_qr.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aircraft_qr_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pilot TEXT,
            ama TEXT,
            faa TEXT,
            phone TEXT,
            builder TEXT,
            model TEXT,
            serial_no TEXT,
            prod_cert TEXT,
            type_cert TEXT
        )
    ''')
    conn.commit()
    conn.close()

# -------------------- CSV Export --------------------
def export_to_csv(data):
    file_exists = os.path.isfile('aircraft_qr.csv')
    with open('aircraft_qr.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                'PILOT', 'AMA#', 'FAA#', 'PH#',
                'BUILDER', 'MODEL', 'SERIAL NO.', 'PROD. CERT.', 'TYPE CERT.'
            ])
        writer.writerow([
            data['PILOT'], data['AMA#'], data['FAA#'], data['PH#'],
            data['BUILDER'], data['MODEL'], data['SERIAL NO.'],
            data['PROD. CERT.'], data['TYPE CERT.']
        ])

# -------------------- API Send --------------------
def send_data_to_api(data):
    url = "http://192.168.1.9:5000/store_data"  # Replace with your actual Flask IP
    try:
        response = requests.post(url, json={"qr_data": data})
        print("✅ API response:", response.json())
    except requests.RequestException as e:
        print("❌ API send error:", e)

# -------------------- Data Parsing --------------------
def parse_data(data):
    try:
        parsed = {}
        for part in data.splitlines():
            if ':' in part:
                key, value = part.split(':', 1)
                parsed[key.strip()] = value.strip()

        required_keys = [
            "PILOT", "AMA#", "FAA#", "PH#", "BUILDER",
            "MODEL", "SERIAL NO.", "PROD. CERT.", "TYPE CERT."
        ]

        for key in required_keys:
            if key not in parsed:
                raise ValueError(f"Missing field: {key}")

        return parsed
    except Exception as e:
        messagebox.showerror("Parsing Error", f"Could not parse QR data:\n{e}")
        return None

# -------------------- Save to DB --------------------
def save_to_database(data):
    conn = sqlite3.connect('aircraft_qr.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO aircraft_qr_data (
            pilot, ama, faa, phone, builder,
            model, serial_no, prod_cert, type_cert
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['PILOT'], data['AMA#'], data['FAA#'], data['PH#'],
        data['BUILDER'], data['MODEL'], data['SERIAL NO.'],
        data['PROD. CERT.'], data['TYPE CERT.']
    ))
    conn.commit()
    conn.close()

# -------------------- Update GUI Fields --------------------
def update_fields(data):
    for key in data:
        if key in entries:
            entries[key].delete(0, tk.END)
            entries[key].insert(0, data[key])

# -------------------- Process Data --------------------
def process_data(data):
    parsed = parse_data(data)
    if parsed:
        update_fields(parsed)
        save_to_database(parsed)
        export_to_csv(parsed)
        send_data_to_api(parsed)
        messagebox.showinfo("Success", "QR data processed and saved successfully!")

# -------------------- Image Scanner --------------------
def scan_qr_from_image():
    path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if not path:
        return
    try:
        image = cv2.imread(path)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        codes = decode(gray, symbols=[ZBarSymbol.QRCODE])
        if codes:
            data = codes[0].data.decode('utf-8')
            process_data(data)
        else:
            messagebox.showwarning("No QR Found", "No QR code detected in the image.")
    except Exception as e:
        messagebox.showerror("Image Error", f"Failed to read image: {e}")

# -------------------- Camera Scanner --------------------
def scan_qr_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Could not access webcam.")
        return

    qr_detected = False
    start_time = time.time()
    timeout = 15  # seconds

    messagebox.showinfo("Scanning", "Align the QR code in front of the camera.")

    while not qr_detected:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        codes = decode(gray, symbols=[ZBarSymbol.QRCODE])

        for code in codes:
            data = code.data.decode('utf-8')
            process_data(data)
            qr_detected = True
            break

        cv2.imshow('QR Scanner - Press Q to quit', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if time.time() - start_time > timeout:
            messagebox.showwarning("Timeout", "QR code not detected in time. Please try again.")
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------- GUI Setup --------------------
app = tk.Tk()
app.title("🛩️ Aircraft QR Code Scanner")
app.geometry("420x550")
app.configure(bg="#f4f4f4")

fields = [
    "PILOT", "AMA#", "FAA#", "PH#",
    "BUILDER", "MODEL", "SERIAL NO.",
    "PROD. CERT.", "TYPE CERT."
]
entries = {}

for field in fields:
    tk.Label(app, text=field, bg="#f4f4f4", font=('Arial', 10, 'bold')).pack()
    entry = tk.Entry(app, width=50)
    entry.pack()
    entries[field] = entry

tk.Button(app, text="📷 Scan from Camera", bg="#4CAF50", fg="white", command=scan_qr_from_camera).pack(pady=10)
tk.Button(app, text="🖼️ Scan from Image", bg="#2196F3", fg="white", command=scan_qr_from_image).pack(pady=5)

# -------------------- Start --------------------
setup_database()
app.mainloop()
