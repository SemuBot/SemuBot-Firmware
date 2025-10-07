import RPi.GPIO as GPIO
import time
import numpy as np

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT)
servo = GPIO.PWM(17, 50)
servo.start(0)
GPIO.setup(22, GPIO.OUT)
servo2 = GPIO.PWM(22, 50)
servo2.start(0)
def map_value(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_min, out_max])

try:
    while True:
        # Take input for angle manually
        angle = int(input("Enter an angle between 0 and 179: "))
        if 0 <= angle <= 179:
            duty = map_value(angle, 0, 179, 2, 12)
            servo.ChangeDutyCycle(duty)
            servo2.ChangeDutyCycle(duty)
            print(f"Servo set to {angle}°")
            time.sleep(1)
            servo.ChangeDutyCycle(0)
            servo2.ChangeDutyCycle(0)

        else:
            print("Invalid angle. Please enter a value between 0 and 179.")
        time.sleep(0.1)
finally:
    servo.stop()
    GPIO.cleanup()
