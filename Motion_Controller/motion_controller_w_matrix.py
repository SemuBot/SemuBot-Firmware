import os
import logging
from datetime import datetime
import RPi.GPIO as GPIO
import pygame
import time
import numpy as np
from pygame.math import Vector2
from servocontroller import ServoController as sc
'''
log_filename = f"logs/motion_controller.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers = [logging.FileHandler(log_filename),logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
'''

def map_range(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_min, out_max])

def wait_for_joystick(target_index=1):
    js = None
    while js is None:
        for event in pygame.event.get():
            if event.type == pygame.JOYDEVICEADDED:
                j = pygame.joystick.Joystick(event.device_index)
                j.init()
                print("Detected:", j.get_name(), "index:", event.device_index)
                if event.device_index == target_index:
                    js = j
                    print("Using joystick", target_index)
        time.sleep(0.1)
    return js


def main():
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    pygame.init()
    pygame.joystick.init()
    joystick = None
    TARGET_INDEX = 1

    joystick = wait_for_joystick(1)

    #joystick = pygame.joystick.Joystick(1) # 0 = genesis, 1 = XBOX
    joystick.init()
    JOYSTICK_THRESHOLD = 0.99
    adjusted_angle = None
    speed_const = 0.5

    GPIO.setmode(GPIO.BCM)
    DUTY_CYCLE = 0

    CHNAGE_DIR_PIN1 = 5 # Kummas suunas mootorid liiguvad
    CHNAGE_DIR_PIN2 = 6
    CHNAGE_DIR_PIN3 = 26
    PWM_PIN1 = 12 # PWM signaal mootoritele
    PWM_PIN2 = 13
    PWM_PIN3 = 19


    GPIO.setup(PWM_PIN1, GPIO.OUT)
    GPIO.setup(PWM_PIN2, GPIO.OUT)
    GPIO.setup(PWM_PIN3, GPIO.OUT)

    pwm1 = GPIO.PWM(PWM_PIN1, 1000)  
    pwm1.start(DUTY_CYCLE)

    pwm2 = GPIO.PWM(PWM_PIN2, 1000)  
    pwm2.start(DUTY_CYCLE)

    pwm3 = GPIO.PWM(PWM_PIN3, 1000)  
    pwm3.start(DUTY_CYCLE)

    GPIO.setup(CHNAGE_DIR_PIN1, GPIO.OUT)
    GPIO.setup(CHNAGE_DIR_PIN2, GPIO.OUT)
    GPIO.setup(CHNAGE_DIR_PIN3, GPIO.OUT)
    V_left = 0
    V_right = 0
    V_back = 0
    rt_value = -1
    lt_value = -1
    matrix = np.array([[-0.33, 0.58, 0.33],
                    [-0.33, -0.58, 0.33],
                    [0.67, 0, 0.33]])
    try:


        while True:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

                elif event.type == pygame.JOYDEVICEREMOVED:
                    print("Joystick disconnected")
                    joystick = None

                elif event.type == pygame.JOYDEVICEADDED:
                    print("Joystick reconnected:", event.device_index)
                    try:
                        js = pygame.joystick.Joystick(event.device_index)
                        js.init()
                        joystick = js
                        print("Reinitialized joystick:", js.get_name())
                    except pygame.error as e:
                        print("Failed to reinit:", e)
            if joystick is None:
                pwm1.ChangeDutyCycle(0)
                pwm2.ChangeDutyCycle(0)
                pwm3.ChangeDutyCycle(0)
                time.sleep(0.05)
                continue
            
            lb_value = joystick.get_button(6)
            rb_value = joystick.get_button(7)
            num_buttons = joystick.get_numbuttons()

            if lb_value:


                lt_value = joystick.get_axis(5)
                rt_value = joystick.get_axis(4)
                right_joystick_y = -(joystick.get_axis(2))  # Assuming Y-axis is inverted
                right_joystick_x = -(joystick.get_axis(3))  # Assuming X-axis is inverted

                OldRange = (1 - 0.15)  
                NewRange = (100 - 1)  
                speed_const = (((max(abs(right_joystick_y), abs(right_joystick_x)) - 0.15) * NewRange) / OldRange) + 1
                #print(right_joystick_x)
                vec = Vector2(right_joystick_x, right_joystick_y)
                magnitude = vec.length()
                if abs(right_joystick_y) < 0.15 and abs(right_joystick_x) < 0.15:
                    adjusted_angle = None
                else:
                    radius, angle = vec.as_polar()
                    adjusted_angle = int((angle + 90) % 360)
                #print(adjusted_angle, rt_value, lt_value)
                if lt_value > -0.98:

                    if adjusted_angle != None:

                        direction = np.array([np.cos(np.radians(adjusted_angle)), np.sin(np.radians(adjusted_angle)), 1])

                        result = np.dot(matrix, direction)

                        V_left = -(speed_const * result[1])
                        V_right = -(speed_const * result[0])
                        V_back = -(speed_const * result[2])
                    else:
                        direction = np.array([0, 0, 1])

                        result = np.dot(matrix, direction)

                        OldRange = (1 - -1)  
                        NewRange = (100 - 1)  
                        speed_const = (((lt_value - -1) * NewRange) / OldRange) + 1

                        V_left = -(speed_const * result[1])
                        V_right = -(speed_const * result[0])
                
                        V_back = -(speed_const * result[2])

                elif rt_value > -0.98:

                    if adjusted_angle != None:
                        direction = np.array([np.cos(np.radians(adjusted_angle)), np.sin(np.radians(adjusted_angle)), -1])

                        result = np.dot(matrix, direction)

                        V_left = -(speed_const * result[1])
                        V_right = -(speed_const * result[0])
                        V_back = -(speed_const * result[2])
                    else:
                        direction = np.array([0, 0, -1])

                        result = np.dot(matrix, direction)

                        OldRange = (1 - -1)  
                        NewRange = (100 - 1)  
                        speed_const = (((rt_value - -1) * NewRange) / OldRange) + 1

                        V_left = -(speed_const * result[1])
                        V_right = -(speed_const * result[0])
                        V_back = -(speed_const * result[2])

                elif rt_value == -1 and lt_value == -1 and adjusted_angle != None:

                    direction = np.array([np.cos(np.radians(adjusted_angle)), np.sin(np.radians(adjusted_angle)), 0])

                    result = np.dot(matrix, direction)

                    V_left = -(speed_const * result[1])
                    V_right = -(speed_const * result[0])
                    V_back = -(speed_const * result[2])


                if rt_value != -1 or lt_value != -1 or adjusted_angle != None:

                    if V_left < 0:
                        GPIO.setup(CHNAGE_DIR_PIN3, GPIO.OUT)
                        GPIO.output(CHNAGE_DIR_PIN3, GPIO.LOW)
                        pwm3.ChangeDutyCycle(np.abs(round(V_left, 2)))
                    else:
                        GPIO.setup(CHNAGE_DIR_PIN3, GPIO.IN)
                        pwm3.ChangeDutyCycle(np.abs(round(V_left, 2)))

                    if V_right < 0:
                        GPIO.setup(CHNAGE_DIR_PIN2, GPIO.OUT)
                        GPIO.output(CHNAGE_DIR_PIN2, GPIO.LOW)
                        pwm2.ChangeDutyCycle(np.abs(round(V_right, 2)))
                    else:
                        GPIO.setup(CHNAGE_DIR_PIN2, GPIO.IN)
                        pwm2.ChangeDutyCycle(np.abs(round(V_right, 2)))

                    if V_back < 0:
                        GPIO.setup(CHNAGE_DIR_PIN1, GPIO.OUT)
                        GPIO.output(CHNAGE_DIR_PIN1, GPIO.LOW)
                        pwm1.ChangeDutyCycle(np.abs(round(V_back, 2)))
                    else:
                        GPIO.setup(CHNAGE_DIR_PIN1, GPIO.IN)
                        pwm1.ChangeDutyCycle(np.abs(round(V_back, 2)))
                else:
                    pwm1.ChangeDutyCycle(0)
                    pwm2.ChangeDutyCycle(0)
                    pwm3.ChangeDutyCycle(0)
            else:
                pwm1.ChangeDutyCycle(0)
                pwm2.ChangeDutyCycle(0)
                pwm3.ChangeDutyCycle(0)

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        pygame.quit()
        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
