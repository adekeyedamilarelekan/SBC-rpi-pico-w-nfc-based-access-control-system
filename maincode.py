# #To extract only the Hashkeys and compare if it is equal
# #to the one written in the card.
# import board
# import busio
# from adafruit_pn532.i2c import PN532_I2C
# import time
# import binascii
# import adafruit_requests
# import wifi
# import socketpool
# import ssl
# 
# # Firebase and WiFi configuration
# FIREBASE_URL = "https://nfc-tecnology-database-default-rtdb.firebaseio.com/users.json"
# DELAY = 0.5
# 
# # WiFi credentials stored in secrets.py
# try:
#     from secrets import secrets
# except ImportError:
#     print("WiFi secrets file is missing!")
#     raise
# 
# # Connect to WiFi
# print("Connecting to WiFi...")
# wifi.radio.connect(secrets["ssid"], secrets["password"])
# print("Connected!")
# 
# # HTTP requests setup
# pool = socketpool.SocketPool(wifi.radio)
# ssl_context = ssl.create_default_context()
# requests = adafruit_requests.Session(pool, ssl_context)
# 
# # NFC configuration
# key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
# MIFARE_CMD_AUTH_B = 0x61
# block_number = 4
# 
# # Create the I2C interface
# i2c = busio.I2C(board.GP5, board.GP4)
# # Create an instance of the PN532 class
# pn532 = PN532_I2C(i2c, debug=False)
# 
# # Configure PN532 to communicate with MiFare cards
# pn532.SAM_configuration()
# 
# 
# def fetch_hash_keys():
#     """Fetch hash keys from Firebase."""
#     try:
#         response = requests.get(FIREBASE_URL)
#         if response.status_code == 200:
#             print("Hash keys fetched successfully!")
#             return response.json()  # Returns the dictionary of users
#         else:
#             print("Failed to fetch hash keys:", response.status_code, response.text)
#             return None
#     except Exception as e:
#         print("Error fetching hash keys:", e)
#         return None
# 
# 
# def extract_payload(data):
#     """Extract the payload from the NFC data."""
#     try:
#         # The payload starts after the language code (e.g., 'en')
#         start_index = data.index(b'T\x02') + 4  # Skip 'T\x02' and language code
#         end_index = data.index(b'\xfe')  # Find the terminator
#         return data[start_index:end_index].decode('utf-8')  # Extract and decode
#     except (ValueError, IndexError) as e:
#         print("Failed to extract payload:", e)
#         return None
# 
# 
# def read_block(hash_keys):
#     """Read NFC block and compare with hash keys."""
#     print('PN532 NFC Module Reader')
#     print('Place the card to be read on the PN532...')
#     while True:
#         uid = pn532.read_passive_target()
#         if uid:
#             print("Card detected! UID:", binascii.hexlify(uid))
#             data = pn532.mifare_classic_read_block(block_number)
#             if data:
#                 print("Data read successfully:", data)
#                 payload = extract_payload(data)
#                 if payload:
#                     print("Extracted payload:", payload)
#                     # Compare with hash keys from Firebase
#                     if any(user['hashkey'] == payload for user in hash_keys.values()):
#                         print("Match found! Hash key is valid.")
#                     else:
#                         print("Hash key does not match.")
#             else:
#                 print("Failed to read data from the card.")
#         time.sleep(DELAY)
# 
# 
# if __name__ == '__main__':
#     # Fetch hash keys from Firebase
#     hash_keys = fetch_hash_keys()
#     if hash_keys:
#         read_block(hash_keys)
#     else:
#         print("Failed to initialize due to missing hash keys.")



##To extract the Hashkeys and compare it with the one written in the card and the name_of_user also. 
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
import binascii
import adafruit_requests
import wifi
import socketpool
import ssl

# Firebase and WiFi configuration
FIREBASE_URL = "https://nfc-tecnology-database-default-rtdb.firebaseio.com/users.json"
DELAY = 0.5

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

# HTTP requests setup
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)

# NFC configuration
key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
MIFARE_CMD_AUTH_B = 0x61
block_number = 4

# Create the I2C interface
i2c = busio.I2C(board.GP5, board.GP4)
# Create an instance of the PN532 class
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

name_of_user = ""


def fetch_hash_keys():
    """Fetch hash keys and names from Firebase."""
    try:
        response = requests.get(FIREBASE_URL)
        if response.status_code == 200:
            print("Hash keys fetched successfully!")
            return response.json()  # Returns the dictionary of users
        else:
            print("Failed to fetch hash keys:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Error fetching hash keys:", e)
        return None


def extract_payload(data):
    """Extract the payload from the NFC data."""
    try:
        # The payload starts after the language code (e.g., 'en')
        start_index = data.index(b'T\x02') + 4  # Skip 'T\x02' and language code
        end_index = data.index(b'\xfe')  # Find the terminator
        return data[start_index:end_index].decode('utf-8')  # Extract and decode
    except (ValueError, IndexError) as e:
        print("Failed to extract payload:", e)
        return None


def format_name(name_of_user):
    """Format the name to fit within 0-19 characters for LCD1602."""
    if not name_of_user:  # Check if name_of_user is missing or None
        name_of_user = "Unknown"
    return "{:<19}".format(name_of_user[:19])  # Truncate and pad with spaces


def read_block(hash_keys):
    """Read NFC block and compare with hash keys."""
    global name_of_user
    print('PN532 NFC Module Reader')
    print('Place the card to be read on the PN532...')
    while True:
        uid = pn532.read_passive_target()
        if uid:
            print("Card detected! UID:", binascii.hexlify(uid))
            data = pn532.mifare_classic_read_block(block_number)
            if data:
                print("Data read successfully:", data)
                payload = extract_payload(data)
                if payload:
                    print("Extracted payload:", payload)
                    # Compare with hash keys from Firebase
                    for user_id, user_data in hash_keys.items():
                        if user_data['hashkey'] == payload:
                            name_of_user = user_data.get('name', "Unknown")  # Fetch name from Firebase
                            name_of_user = format_name(name_of_user)  # Format it for LCD1602
                            print(f"Match found! Welcome, {name_of_user.strip()}.")
                            break
                    else:
                        name_of_user = format_name("Access Denied")  # Handle no match
                        print("Hash key does not match.")
                        print("name_of_user: ", name_of_user)

            else:
                print("Failed to read data from the card.")
        time.sleep(DELAY)


if __name__ == '__main__':
    # Fetch hash keys from Firebase
    hash_keys = fetch_hash_keys()
    if hash_keys:
        name_of_user = "Initializing..."+"{:<19}".format(name_of_user[:19])  # Default message
        read_block(hash_keys)
    else:
        print("Failed to initialize due to missing hash keys.")
