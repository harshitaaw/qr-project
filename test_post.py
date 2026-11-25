import requests

# URL must match the Flask route
url = "http://192.168.1.9:5000/store_data"

# Sample QR data to send
data = {
    "qr_data": {
        "name": "Boeing 737",
        "id": "AC1234",
        "location": "Hangar 5"
    }
}

response = requests.post(url, json=data)
print("Response:", response.status_code)
print("Data:", response.text)
