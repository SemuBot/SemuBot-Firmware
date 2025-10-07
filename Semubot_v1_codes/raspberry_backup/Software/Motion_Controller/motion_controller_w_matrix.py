import os
import RPi.GPIO as GPIO
import pygame
import numpy as np
import time
from pygame.math import Vector2


def map_range(value, in_min, in_max, out_min, out_max):
    return np.interp(value, [in_min, in_max], [out_min, out_max])




def main():
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    pygame.init()
    pygame.joystick.init()

    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    JOYSTICK_THRESHOLD = 0.99
    adjusted_angle = None
    speed_const = 0.5

    GPIO.setmode(GPIO.BCM)
    CHNAGE_DIR_PIN1 = 5
    CHNAGE_DIR_PIN2 = 6
    CHNAGE_DIR_PIN3 = 26
    PWM_PIN1 = 12
    PWM_PIN2 = 13
    PWM_PIN3 = 19
    BUTTON_PIN = 4
    DUTY_CYCLE = 0  
    SERVO_PIN1 = 17
    SERVO_PIN2 = 22
    SERVO_PIN3 = 24
    SERVO_PIN4 = 25
    freq = 50
    
    GPIO.setup([SERVO_PIN1, SERVO_PIN2, SERVO_PIN3, SERVO_PIN4], GPIO.OUT)
    servo1 = GPIO.PWM(SERVO_PIN1, freq) 
    servo2 = GPIO.PWM(SERVO_PIN2, freq)
    servo3 = GPIO.PWM(SERVO_PIN3, freq)
    servo4 = GPIO.PWM(SERVO_PIN4, freq)

    GPIO.setup(PWM_PIN1, GPIO.OUT)
    GPIO.setup(PWM_PIN2, GPIO.OUT)
    GPIO.setup(PWM_PIN3, GPIO.OUT)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pwm1 = GPIO.PWM(PWM_PIN1, 1000)  
    pwm1.start(DUTY_CYCLE)

    pwm2 = GPIO.PWM(PWM_PIN2, 1000)  
    pwm2.start(DUTY_CYCLE)

    pwm3 = GPIO.PWM(PWM_PIN3, 1000)  
    pwm3.start(DUTY_CYCLE)
    servo1.start(3)  # Neutral position ???
    servo2.start(3)
    servo3.start(3)
    servo4.start(3)


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
    last_servo_time = None
    servo_duration = 0.5  
    try:


        while True:

            while (GPIO.input(BUTTON_PIN) == GPIO.LOW):
                lb_value = joystick.get_button(6)
                rb_value = joystick.get_button(7)
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return
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
                elif rb_value:
                    print("RBBB")
                    left_x = joystick.get_axis(0)
                    left_y = joystick.get_axis(1)
                    right_x = joystick.get_axis(2)
                    right_y = joystick.get_axis(3)
                    #print("Left_x: ",left_x)
                    #print("Left_y: ",left_y)
                    #print("Right_x: ",right_x)
                    #print("Right_y: ",right_y)
                    dead_zone = 0.3  
                    left_x = joystick.get_axis(0) if abs(joystick.get_axis(0)) > dead_zone else 0
                    left_y = joystick.get_axis(1) if abs(joystick.get_axis(1)) > dead_zone else 0
                    right_x = joystick.get_axis(2) if abs(joystick.get_axis(2)) > dead_zone else 0
                    right_y = joystick.get_axis(3) if abs(joystick.get_axis(3)) > dead_zone else 0
                    min_val = 2
                    max_val = 12
                    servo1_angle = map_range(left_x, -1, 1, min_val, max_val)
                    servo2_angle = map_range(left_y, -1, 1, min_val, max_val)
                    servo3_angle = map_range(right_x,-1, 1,min_val, max_val)
                    servo4_angle = map_range(right_y, -1, 1, min_val, max_val)
                    print("Servo1: ",servo1_angle)
                    print("Servo2: ",servo2_angle)
                    last_servo_time = time.time()
                    servo1.ChangeDutyCycle(servo1_angle)
                    servo2.ChangeDutyCycle(servo2_angle)
                    servo3.ChangeDutyCycle(servo3_angle)
                    servo4.ChangeDutyCycle(servo4_angle)

                    while time.time() - last_servo_time > servo_duration:
                        servo1.ChangeDutyCycle(0)
                        servo2.ChangeDutyCycle(0)
                        servo3.ChangeDutyCycle(0)
                        servo4.ChangeDutyCycle(0)
                else:

                    pwm1.ChangeDutyCycle(0)
                    pwm2.ChangeDutyCycle(0)
                    pwm3.ChangeDutyCycle(0)
                    servo1.ChangeDutyCycle(0)
                    servo2.ChangeDutyCycle(0)
                    servo3.ChangeDutyCycle(0)
                    servo4.ChangeDutyCycle(0)
            print("Stop button is pressed...")

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
