import board
import busio
from adafruit_pn532.i2c import PN532_I2C
import time
import binascii
import sys

key = b'\xFF\xFF\xFF\xFF\xFF\xFF'
MIFARE_CMD_AUTH_B = 0x61
block_number = 4

HEADER = b'BG'

DELAY = 0.5

# Create the I2C interface
i2c = busio.I2C(board.GP5, board.GP4)
# Create an instance of the PN532 class
pn532 = PN532_I2C(i2c, debug=False)

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()


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


def read_block():
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
                    # Compare with hash key
                    hashkey = "abcde"  # Example hash key
                    if payload == hashkey:
                        print("Match found! Hash key is valid.")
                    else:
                        print("Hash key does not match.")
            else:
                print("Failed to read data from the card.")
        time.sleep(DELAY)

if __name__ == '__main__':
     read_block()
