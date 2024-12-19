import wifi
import ssl
import socketpool
import adafruit_requests

# WiFi credentials stored in secrets.py
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets file is missing!")
    raise

# Connect to WiFi
print("Connecting to WiFi...")
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected!")

# Initialize HTTP session with SSL context
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# Firebase Realtime Database URL
FIREBASE_URL = "https://nfc-tecnology-database-default-rtdb.firebaseio.com"

# Data to upload
users_data = {
    "user1": {"name": "John Doe", "hashkey": "abcd1234"},
    "user2": {"name": "Jane Smith", "hashkey": "xyz5678"}
}

# Upload data to Firebase
response = requests.put(FIREBASE_URL + "/users.json", json=users_data)
print("Data upload response:", response.text)
