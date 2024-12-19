# For CircuitPython
import time
import board
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


# Function to control LEDs
def led_control():
    # Turn on usrValidLed and wait
    usrValidLed.value = True
    time.sleep(2)

    # Turn off usrValidLed and turn on usrNotValidLed
    usrValidLed.value = False
    usrNotValidLed.value = True
    time.sleep(2)

    # Turn both LEDs off
    usrNotValidLed.value = False
    time.sleep(2)

# Main loop
while True:
    led_control()
