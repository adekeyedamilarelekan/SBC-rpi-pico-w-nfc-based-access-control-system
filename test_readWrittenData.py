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


def read_block():
# Step 1, wait for card to be present.
    print('PN532 NFC Module Writer')
    print('')
    print('== STEP 1 =========================')
    print('Place the card to be written on the PN532...')
    uid = pn532.read_passive_target()
    while uid is None:
        uid = pn532.read_passive_target()
        print(uid)
# 
#         if pn532.mifare_classic_authenticate_block(uid, block_number, MIFARE_CMD_AUTH_B, key):
#                     print("Authentication successful!")
#         else:
#             print("Authentication failed.")

        # Attempt to read data from the card
        data = pn532.mifare_classic_read_block(block_number)  # Reading block 4, change as needed

        if data is not None:
            print("Data read successfully:", data)
        else:
            print("Failed to read data from the card")


if __name__ == '__main__':
     read_block()
