import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface

# Set up shared I2C bus on GPIO4 (SDA) and GPIO5 (SCL)
i2c = busio.I2C(board.GP5, board.GP4)

# Initialize PN532 on the shared I2C bus
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
lcd.print("Hello World!")
print("LCD initialized and message displayed.")


def normalize_uid(uid):
    """Normalize the UID to 7 bytes by padding if necessary."""
    if len(uid) == 4:
        uid.extend(['0x00', '0x00', '0x00'])  # Pad with '0x00' for 7-byte length
    return tuple(uid)

# Store the current state of card detection
card_detected = False

while True:
    # Try to read an NFC card
    uid = pn532.read_passive_target(timeout=0.5)
    
    if uid:
        uid_hex = [hex(i) for i in uid]
        normalized_uid = normalize_uid(uid_hex)
        print("Found card with UID:", normalized_uid)

        if normalized_uid in registered_uids:
            user_name = registered_uids[normalized_uid]
            
            # Check if the user is already signed in
            if user_name in user_status and user_status[user_name] == "signed in":
                lcd.clear()
                lcd.print(f"Already signed in.\nRemove card.")
                print(f"{user_name} is already signed in. Waiting for card removal.")
                # Indicate that a card is detected, and the user should remove it
                card_detected = True
                while card_detected:
                    # Keep checking for card removal
                    if not pn532.read_passive_target(timeout=0.5):
                        card_detected = False
                        print(f"{user_name} removed card. Sign out allowed.")
                        user_status[user_name] = "signed out"
                    time.sleep(0.1)  # Small delay to allow for checking

            # Check if the user is already signed out
            elif user_name in user_status and user_status[user_name] == "signed out":
                lcd.clear()
                lcd.print(f"Already signed out.\nRemove card.")
                print(f"{user_name} is already signed out. Waiting for card removal.")
                # Indicate that a card is detected, and the user should remove it
                card_detected = True
                while card_detected:
                    # Keep checking for card removal
                    if not pn532.read_passive_target(timeout=0.5):
                        card_detected = False
                        print(f"{user_name} removed card. Sign in allowed.")
                        user_status[user_name] = "signed in"
                    time.sleep(0.1)  # Small delay to allow for checking

            else:
                # Sign the user in or out based on the previous status
                if user_name not in user_status or user_status[user_name] == "signed out":
                    user_status[user_name] = "signed in"
                    lcd.clear()
                    lcd.print(f"{user_name} signed in")
                    print(f"{user_name} signed in")
                else:
                    user_status[user_name] = "signed out"
                    lcd.clear()
                    lcd.print(f"{user_name} signed out")
                    print(f"{user_name} signed out")

                # Wait for the card removal before allowing another sign-in/sign-out attempt
                card_detected = True
                while card_detected:
                    # Keep checking for card removal
                    if not pn532.read_passive_target(timeout=0.5):
                        card_detected = False
                        print(f"Card removed. Ready for next action.")
                    time.sleep(0.1)  # Small delay to allow for checking

                time.sleep(0.5)  # Pause before allowing the next scan

        else:
            lcd.clear()
            lcd.print("User not registered")
            print("User not registered")

    else:
        lcd.clear()
        lcd.print("Waiting for card")
        print("No card detected.")
    
    time.sleep(0.5)

