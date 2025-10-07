#!/usr/bin/env python3
"""
Simple script to move Motor 1 left and wait for response
"""

import serial
import time

# Configuration
PORT = '/dev/ttyACM0'  # Change this to your STM32's port
BAUDRATE = 115200

def send_command_and_wait(ser, command, description=""):
    """Send a command and wait for STM32 response"""
    print(f"\nSending: {description}")
    print(f"Command: {command.strip()}")
    
    # Send command
    ser.write(command.encode())
    ser.flush()
    
    # Wait for response
    print("Waiting for response...")
    start_time = time.time()
    timeout = 5  # 5 second timeout
    
    while time.time() - start_time < timeout:
        if ser.in_waiting > 0:
            response = ser.readline().decode().strip()
            if response:
                print(f"STM32 Response: {response}")
                return response
        time.sleep(0.01)
    
    print("No response received (timeout)")
    return None

def main():
    try:
        # Connect to STM32
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"Connected to {PORT}")
        time.sleep(2)  # Give STM32 time to initialize
        
        # Clear any existing data in buffer
        ser.reset_input_buffer()
        
        # Command to move Motor 1 left
        cmd = "{linear_x:0.00,linear_y:-0.50,linear_z:0.00,angular_x:0.00,angular_y:0.00,angular_z:0.00}\n"
        response = send_command_and_wait(ser, cmd, "Move Motor 1 Left")
        
        # Wait a bit
        time.sleep(2)
        
        # Stop motors
        stop_cmd = "{linear_x:0.00,linear_y:0.00,linear_z:0.00,angular_x:0.00,angular_y:0.00,angular_z:0.00}\n"
        response = send_command_and_wait(ser, stop_cmd, "Stop Motors")
        
        ser.close()
        print("\nTest completed!")
        
    except serial.SerialException as e:
        print(f"Serial error: {e}")
        print("\nTry checking:")
        print("- Is the STM32 connected?")
        print("- Is the port correct? (try /dev/ttyACM1, COM3, etc.)")
        print("- Is another program using the port?")
    except KeyboardInterrupt:
        print("\nStopped by user")
        try:
            ser.write("{linear_x:0.00,linear_y:0.00,linear_z:0.00,angular_x:0.00,angular_y:0.00,angular_z:0.00}\n".encode())
            ser.close()
        except:
            pass

if __name__ == "__main__":
    main()
