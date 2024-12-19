import time
import board
import pwmio

# Initialize PWM for servo on GP15
servo = pwmio.PWMOut(board.GP15, frequency=50)

# Calibrate these values to your specific servo's pulse width range
MIN_DUTY = 1000  # Adjust based on your servo's min pulse width
MAX_DUTY = 9000  # Adjust based on your servo's max pulse width

def set_servo_angle_slowly(target_angle, delay=0.03):
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
    # Set duty cycle to 0 to turn off PWM and stop vibration
    servo.duty_cycle = 0
    
    
# while True:

# Test slow movement without overshooting
set_servo_angle_slowly(90)  # Slowly move to 90 degrees
time.sleep(1)

set_servo_angle_slowly(0)  # Slowly return to 0 degrees
stop_servo()  # Turn off PWM signal to prevent vibrations
time.sleep(1)

