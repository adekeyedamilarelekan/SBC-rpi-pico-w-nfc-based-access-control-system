#Damilare Lekan Adekeye
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
import binascii
import adafruit_requests
import wifi
import socketpool
import ssl
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
import pwmio
import digitalio


# Setup for LEDs on GP2, GP3, GP6, and GP22.
usrValidLed = digitalio.DigitalInOut(board.GP2)
usrValidLed.direction = digitalio.Direction.OUTPUT

usrNotValidLed = digitalio.DigitalInOut(board.GP3)
usrNotValidLed.direction = digitalio.Direction.OUTPUT

WiFI_Led = digitalio.DigitalInOut(board.GP6)
WiFI_Led.direction = digitalio.Direction.OUTPUT

Buzzer = digitalio.DigitalInOut(board.GP22)
Buzzer.direction = digitalio.Direction.OUTPUT


# Firebase and WiFi configuration
FIREBASE_URL = "https://nfc-tecnology-database-default-rtdb.firebaseio.com/users.json"


DELAY = 0.5

# NFC configuration
key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
MIFARE_CMD_AUTH_B = 0x61
block_number = 4

# Create the I2C interface
i2c = busio.I2C(board.GP5, board.GP4)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()
print("PN532 NFC reader initialized and ready to scan.")


# Initialize LCD on the shared I2C bus
i2c.try_lock()
address1 = i2c.scan()[0]
address2 = i2c.scan()[1]
print(f"Found PN532 at address1: 0x{address1:X}")
print(f"Found LCD at address2: 0x{address2:X}")
i2c.unlock()


lcd = LCD(I2CPCF8574Interface(i2c, address2), num_rows=2, num_cols=16)
lcd.clear()
lcd.print("    Welcome!    ")
time.sleep(2)
print("LCD initialized and message displayed.")


# WiFi credentials stored in secrets.py
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets file is missing!")
    raise

# Connect to WiFi
print("Connecting to WiFi...")
lcd.clear()
lcd.print("Connecting WiFi!")
try:
    wifi.radio.connect(secrets["ssid"], secrets["password"])
    lcd.clear()
    lcd.print("WiFi Connected!!")
    Buzzer.value = True #Buzzer ON
    WiFI_Led.value = True #WiFi LED ON
    print("Connected!")
    time.sleep(0.5) #0.7secs
    Buzzer.value = False #Buzzer OFF
except Exception as e:
    lcd.clear()
    lcd.print("WiFi is NOT\nConnected!!!")
    pass

# HTTP requests setup
pool = socketpool.SocketPool(wifi.radio)
ssl_context = ssl.create_default_context()
requests = adafruit_requests.Session(pool, ssl_context)


# Servo motor configuration
servo = pwmio.PWMOut(board.GP15, frequency=50)

# Servo calibration values
MIN_DUTY = 1000  # Minimum pulse width for your servo
MAX_DUTY = 9000  # Maximum pulse width for your servo

# Global variables
name_of_user = ""

# Main loop
last_check_time = time.monotonic()  # Initialize last check time to the current time



# Check internet connection via DNSs
def check_internet():
    try:
        pool = socketpool.SocketPool(wifi.radio)
        # Perform a DNS lookup
        addr_info = pool.getaddrinfo("google.com", 80)
        if addr_info:
            print("Internet connected! (Check every 5secs the internet/WiFi if it's connected/disconnected).")
            return True
        else:
            print("No internet connection.")
            return False
    except Exception as e:
        print("No internet connection:", e)
        return False


    
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
        lcd.clear()
        Buzzer.value = True
        usrNotValidLed.value = True
        lcd.print("Access Denied.")
        time.sleep(2)
        Buzzer.value = False
        usrNotValidLed.value = False
        lcd.clear()
        lcd.print("No Data in Card\nPlease Register!")
        time.sleep(2)
        return None


def format_name(name_of_user):
    """Format the name to fit within 0-19 characters for LCD1602."""
    if not name_of_user:  # Check if name_of_user is missing or None
        name_of_user = "Unknown"
    return "{:<19}".format(name_of_user[:19])  # Truncate and pad with spaces


def set_servo_angle_slowly(target_angle, delay=0.03):
    """Gradually move the servo to the target angle."""
    # Get current angle based on duty cycle or assume it starts at 0 degrees
    current_duty = servo.duty_cycle
    current_angle = int((current_duty - MIN_DUTY) * 180 / (MAX_DUTY - MIN_DUTY)) if current_duty > 0 else 0

    # Determine direction and move gradually
    step = 1 if target_angle > current_angle else -1
    for angle in range(current_angle, target_angle + step, step):
        duty = int(MIN_DUTY + (angle / 180) * (MAX_DUTY - MIN_DUTY))
        
        # Only set duty cycle within valid range
        if MIN_DUTY <= duty <= MAX_DUTY:
            servo.duty_cycle = duty
        time.sleep(delay)  # Delay for smoother movement


def stop_servo():
    """Stop the servo by turning off the PWM signal."""
    servo.duty_cycle = 0
    print("Servo stopped.")


def unlock_door():
    """Unlock the door by moving the servo."""
    print("Unlocking door...")
    set_servo_angle_slowly(90)  # Move servo to open position
    time.sleep(3)  # Keep the door unlocked for a short time
    set_servo_angle_slowly(0)  # Return servo to default position
    stop_servo()


def read_block(hash_keys):
    """Read NFC block and compare with hash keys."""
    global name_of_user
    global current_time
    global last_check_time
    print('PN532 NFC Module Reader')
    print('Place the card to be read on the PN532...')
    while True:
        current_time = time.monotonic()  # Get the current time in seconds
        if current_time - last_check_time >= 5:  # Check every 5 seconds
            if check_internet():
                WiFI_Led.value = True  # Turn LED ON if connected
            else:
                WiFI_Led.value = False  # Turn LED OFF if not connected
            last_check_time = current_time  # Update the last check time
      
        uid = pn532.read_passive_target()
        if uid:
            uid_hex = [hex(i) for i in uid]
            print("Card detected! UID:", uid_hex)
            data = pn532.mifare_classic_read_block(block_number)
            if data:
                print("Data read successfully:", data)
                payload = extract_payload(data)
                if payload:
                    print("Extracted payload:", payload)
                    # Compare with hash keys from Firebase
                    for user_id, user_data in hash_keys.items():
                        if user_data['hashkey'] == payload:
                            name_of_user = user_data.get('name', "Unknown")
                            name_of_user = format_name(name_of_user)  # Format for LCD1602
                            lcd.clear()
                            lcd.print(f"Welcome,\n{name_of_user.strip()}")
                            print(f"Match found! Welcome, {name_of_user.strip()}.")
                            usrValidLed.value = True  #ON the LED Indicator.
                            unlock_door()
                            break
                    else:
                        lcd.clear()
                        lcd.print("Access Denied.")
                        usrNotValidLed.value = True
                        Buzzer.value = True
                        print("Hash key does not match.")
                        time.sleep(1.5)
                        usrNotValidLed.value = False     #OFF the LED. indicator.                       
                        Buzzer.value = False           #OFF the Buzzer indicator.
                        lcd.clear()
                        lcd.print("Record Mismatch\nin Our Database!")
                        time.sleep(1)
            else:
                print("Failed to read data from the card.")
                lcd.clear()
                lcd.print("Access Denied.")
                usrNotValidLed.value = True
                Buzzer.value = True
                time.sleep(1.5)
                usrNotValidLed.value = False     #OFF the LED. indicator.                       
                Buzzer.value = False           #OFF the Buzzer indicator.
                lcd.clear()
                lcd.print("NFC Card Error!\nNot Writable!")
                time.sleep(1)
                
        else:
            lcd.clear()
            lcd.print("Scan Your Card \nfor Access!!!")
            print("No card detected.")
            usrValidLed.value = False     #OFF the LED. indicator.                       
            usrNotValidLed.value = False     #OFF the LED. indicator.                       
            Buzzer.value = False           #OFF the Buzzer indicator.


        time.sleep(DELAY)


if __name__ == '__main__':
    # Fetch hash keys from Firebase
    hash_keys = fetch_hash_keys()
    if hash_keys:
        name_of_user = format_name("Initializing...")  # Default message
        lcd.clear()
        lcd.print("System is Ready.")
        time.sleep(2)
        read_block(hash_keys)
    else:
        lcd.clear()
        lcd.print("Initialization\nFailed!")
        time.sleep(2)
        lcd.print("Missing hashkey!")
        print("Failed to initialize due to missing hash keys.")
