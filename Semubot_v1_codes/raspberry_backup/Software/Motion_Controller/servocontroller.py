import serial
import serial.tools.list_ports as lp
import time
import numpy as np
import logging


class ServoController:
    """
    A class to control individual servos with open/close functionality
    and methods to set specific servo positions.
    """

    def __init__(self, baudrate=19200, automatic_con=True, target_device="USB VID:PID=04D8:00DD"):
        self.baudrate = baudrate
        self.ser = None
        self.connected = False
        self.auto_con = automatic_con
        self.device = target_device

        #Initial servo values (neutral position)
        self.servo_positions = [990,900,900,900,900]
        self.c_lim = 1000
        self.timer = 1 

        print("Available ports:")
        
    def open(self):
        """
        Open serial connection to the servo controller.
        """
        if self.connected:
            print("Already connected.")
            return True
        ports = list(lp.comports())
        devices = {}
        serial_port = None
        #Try to connect to any available COM port
        for port, _,  hwid in sorted(ports):
            devices[hwid] = port
            print(hwid, port)
        for hwid, serial_port in devices.items():
            if hwid == self.device:
                break

        if serial_port == None:
            raise SerialPortNotFound

        try:
            print(f"Trying to connect to port {self.device}")
            self.ser = serial.Serial(serial_port, baudrate=self.baudrate)
            print(f"Connected to port: {self.device}")
            self.connected = True
            self._send_initial_positions()
            return True
        except serial.SerialException as e:
            print(f"Failed to connected to {self.device}: {e}")


        return False

    def close(self):
        """ Close serial connection to servo controller."""
        if self.connected and self.ser:
            try:
                self.ser.close()
                print("Serial connection closed.")
                self.connected = False
                return True
            except Exception as e:
                print(f"Error closing connection: {e}")
                return False
        else:
            print("No active connection to close.")
            return True

    def _send_initial_positions(self):
        """Send initial servo positions to set up the arm."""
        self._send_servo_data()

    def _format_servo_data(self):
        """Format servo data for transmission to controller."""

        debug = 0
        data = np.array([
            self.servo_positions +
            [self.c_lim] * 5 +
            [self.timer] * 5 +
            [debug, self.timer]
        ], dtype=np.uint16)

        return data

    def _send_servo_data(self, wait_for_completion=True):
        """Send current servo positions to the controller."""
        if not self.connected or not self.ser:
            print("Error: Not connected to servo controller.")
            return False

        try:
            data = self._format_servo_data()
            data_bytes = bytearray(data[0,0:-1])
            print(f"Sending servo data: {data_bytes}")
            code = self.ser.write(data_bytes)
            print(f"Write done. Code: {code}")

            # Only wait if explicitly requested (for real-time control, skip this)
            if wait_for_completion:
                time.sleep(self.timer/1000.0)
            else:
                time.sleep(0.01)

            return True

        except Exception as e:
            print(f"Error sending servo data: {e}")
            return False

    def move_servo_realtime(self, servo_number, movement_amount):
        """
        Move a servo for real-time control without waiting for completion.
        Optimized for rapis successive movements.
        """

        if servo_number<1 or servo_number > 5:
            print("Error: Servo number must be between 1 and 5")
            return False

        current_position = self.servo_positions[servo_number - 1]
        new_position = current_position + movement_amount
        min_position = 300
        max_position = 1500

        new_position = max(min_position, min(max_position, new_position))
        self.servo_positions[servo_number - 1] = new_position
        print(f"Moved {servo_number} to {new_position}")
        return self._send_servo_data(wait_for_completion=False)

    def set_servo(self, servo_number, position, movement_time=None):
        """
        Set a specific servo to a specific position.


        Args:
            servo_number (int): Servo number(1-5)
            position (int): Targe position
            movement_time (int, optional): Time for movement in ms
        """
        if servo_number < 1 or servo_number > 5:
            print("Error Servo number must be between 1 and 5")
            return False

        if movement_time is not None:
            self.timer = movement_time

        self.servo_positions[servo_number - 1] = position
        print(f"Moved servo {servo_number} to {position}")

        return self._send_servo_data()

    def set_servo_1(self, position, movement_time=None):
        return self.set_servo(1, position, movement_time)

    def set_servo_2(self, position, movement_time=None):
        return self.set_servo(2, position, movement_time)

    def set_servo_3(self, position, movement_time=None):
        return self.set_servo(3, position, movement_time)

    def set_servo_4(self, position, movement_time=None):
        return self.set_servo(4, position, movement_time)

    def set_servo_5(self, position, movement_time=None):
        return self.set_servo(5, position, movement_time)

    def move_servo(self, servo_number, movement_amount, movement_time=None):
        """
        Move a specific servo by a relative amount from its current position

        Args:
            servo_number (int): servo number (1-5)
            movement_amount (int): amount to move (positive or negative)
            movement_time (int, optional): time for movement in ms
        """

        if servo_number < 1 or servo_number > 5:
            print("Error: Servo number must be between 1 and 5")
            return False

        current_position = self.serv_positions[servo_number - 1]

        new_position = current_position + movement_amount
        min_position = 0
        max_position = 1800
        new_position = max(new_position, min_position)
        new_position = min(new_position, max_position)

        print(f"Moving servo {servo_number} from {current_position} by {movement_amount} to {new_position}")

        return self.set_servo(servo_number, new_position, movement_time)

    def set_all_servos(self, positions, movement_time=None):
        """
        Set all servos to specified positions.

        Args:
            positoins (list): List of 5 positions for servos 1-5
            movement_time (int, optional): Time for movement in ms
        """
        if len(positions)!=5:
            print("Error: Must provide exact 5 positions")
            return False

        if movement_time != None:
            self.timer = movement_time

        self.servo_positions = positions.copy()

        return self._send_servo_data()

    def get_servo_position(self, servo_number):
        if servo_number<1 or servo_number>5:
            print("Error: servo number must be between 1 and 5")
            return None
        return self.servo_positions[servo_number-1]

    def get_all_positions(self):
        return self.servo_positions.copy()

    def reset_to_neutral(self, movement_time=1000):
        neutral_positions = [900,900,900,900,900]
        return self.set_all_servos(neutral_positions, movement_time)

    def read_response(self, timeout=1):
        """Read a line or available data from the servo controller."""
        if not self.connected or not self.ser:
            print("Error: Not connected to servo controller.")
            return None

        self.ser.timeout = timeout
        try:
            response = self.ser.readline().decode(errors="ignore").strip()
            if response:
                print(f"Received: {response}")
                return response
            else:
                print("No data received.")
                return None
        except Exception as e:
            print(f"Error reading from serial: {e}")
            return None

