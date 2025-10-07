#!/usr/bin/env python3
"""
Simple script to move Motor 1 left
"""

import serial
import time

# Configuration
PORT = '/dev/ttyACM0'
BAUDRATE = 115200

def send_motor1_left():
    try:
        # Connect to STM32
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Connected to {PORT}")
        
        # Command to move left (negative linear_y should move motor 1)
        cmd = "{linear_x:2.00,linear_y:-2.50,linear_z:2.00,angular_x:2.00,angular_y:2.00,angular_z:2.00}\n"
        
        print("Sending command to move Motor 1 left...")
        ser.write(cmd.encode())
        ser.flush()
        
        time.sleep(3)
        
        # Stop motors
        stop_cmd = "{linear_x:0.00,linear_y:0.00,linear_z:0.00,angular_x:0.00,angular_y:0.00,angular_z:0.00}\n"
        print("Stopping motors...")
        ser.write(stop_cmd.encode())
        ser.flush()
        
        # Read any responses
        time.sleep(0.5)
        while ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            print(f"STM32: {response}")
        
        ser.close()
        print("Done!")
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
    except KeyboardInterrupt:
        print("\nStopped by user")
        try:
            ser.write(stop_cmd.encode())
            ser.close()
        except:
            pass

if __name__ == "__main__":
    send_motor1_left()
