import serial
import serial.tools.list_ports as lp
import time
import numpy as np

class ServoController:
    """
    A class to control individual servos with open/close functionality
    and methods to set specific servo positions.
    """
    
    def __init__(self, baudrate=19200, automatic_con=True, target_device="COM5"):
        self.baudrate = baudrate
        self.ser = None
        self.ports = list(lp.comports())
        self.connected = False
        self.auto_con = automatic_con
        self.device = target_device
        
        # Initial servo values (neutral position)
        self.servo_positions = [900, 900, 900, 900, 900]  # Servos 1-5
        self.c_lim = 3000  # Current limit for all servos
        self.timer = 1  # Default movement time in ms
        
        print("Available ports:")
        for port in self.ports:
            print(f"{port.device} : {port.name}, [{port.description}]")
    
    def open(self):
        """Open serial connection to the servo controller."""
        if self.connected:
            print("Already connected.")
            return True
            
        if self.auto_con:
            # Try to connect to any available COM port
            for port in self.ports:
                if str(port.device).startswith("COM") and not self.connected:
                    try:
                        print(f"Trying to connect to port {port.device}")
                        self.ser = serial.Serial(port.device, baudrate=self.baudrate)
                        print(f"Connected to port: {port.device}")
                        self.connected = True
                        self._send_initial_positions()
                        return True
                    except serial.SerialException as e:
                        print(f"Failed to connect to {port.device}: {e}")
                        continue
        else:
            # Try to connect to specific device
            try:
                print(f"Trying to connect to port {self.device}")
                self.ser = serial.Serial(self.device, baudrate=self.baudrate)
                print(f"Connected to port: {self.device}")
                self.connected = True
                self._send_initial_positions()
                return True
            except serial.SerialException as e:
                print(f"Failed to connect to {self.device}: {e}")
                return False
        
        if not self.connected:
            print("Could not find suitable COM port. Check your device or port name")
            return False
    
    def close(self):
        """Close serial connection to the servo controller."""
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
        print("Setting initial servo positions...")
        self._send_servo_data()
    
    def _format_servo_data(self):
        """Format servo data for transmission to the controller."""
        # Format: S1,S2,S3,S4,S5,c_lim,c_lim,c_lim,c_lim,c_lim,timer,timer,timer,timer,timer,debug,timer
        debug = 0
        data = np.array([
            self.servo_positions + 
            [self.c_lim] * 5 + 
            [self.timer] * 5 + 
            [debug, self.timer]
        ], dtype=np.uint16)
        
        return data
    
    # def _send_servo_data(self):
    #     """Send current servo positions to the controller."""
    #     if not self.connected or not self.ser:
    #         print("Error: Not connected to servo controller.")
    #         return False
            
    #     try:
    #         data = self._format_servo_data()
    #         data_bytes = bytearray(data[0, 0:-1])  # Exclude the last timer value
    #         print(f"Sending servo data: {data_bytes}")
    #         code = self.ser.write(data_bytes)
    #         print(f"Write done. Code: {code}")
            
    #         # Wait for movement to complete
    #         time.sleep(self.timer / 1000.0)
    #         return True
    #     except Exception as e:
    #         print(f"Error sending servo data: {e}")
    #         return False
    
    def _send_servo_data(self, wait_for_completion=True):
        """Send current servo positions to the controller."""
        if not self.connected or not self.ser:
            print("Error: Not connected to servo controller.")
            return False
            
        try:
            data = self._format_servo_data()
            data_bytes = bytearray(data[0, 0:-1])  # Exclude the last timer value
            print(f"Sending servo data: {data_bytes}")
            code = self.ser.write(data_bytes)
            print(f"Write done. Code: {code}")
            
            # Only wait if explicitly requested (for real-time control, skip this)
            if wait_for_completion:
                time.sleep(self.timer / 1000.0)
            else:
                time.sleep(0.01)  # Short delay to allow command processing
            return True
        except Exception as e:
            print(f"Error sending servo data: {e}")
            return False

    def move_servo_realtime(self, servo_number, movement_amount):
        """
        Move a servo for real-time control without waiting for completion.
        Optimized for rapid successive movements.
        """
        if servo_number < 1 or servo_number > 5:
            print("Error: Servo number must be between 1 and 5")
            return False
        
        # Get current position
        current_position = self.servo_positions[servo_number - 1]
        
        # Calculate new position
        new_position = current_position + movement_amount
        
        min_position = 0
        max_position = 1800
        
        # Clamp to limits
        new_position = max(min_position, min(max_position, new_position))
        
        # Update position
        self.servo_positions[servo_number - 1] = new_position
        
        # Send immediately without waiting
        return self._send_servo_data(wait_for_completion=False)
    
    def set_servo(self, servo_number, position, movement_time=None):
        """
        Set a specific servo to a specific position.
        
        Args:
            servo_number (int): Servo number (1-5)
            position (int): Target position (typically 500-2500 for servo range)
            movement_time (int, optional): Time for movement in milliseconds
        """
        if servo_number < 1 or servo_number > 5:
            print("Error: Servo number must be between 1 and 5")
            return False
            
        if movement_time is not None:
            self.timer = movement_time
            
        # Update the servo position
        self.servo_positions[servo_number - 1] = position
        print(f"Setting servo {servo_number} to position {position}")
        
        # Send the updated positions
        return self._send_servo_data()
    
    def set_servo_1(self, position, movement_time=None):
        """Set servo 1 to specified position."""
        return self.set_servo(1, position, movement_time)
    
    def set_servo_2(self, position, movement_time=None):
        """Set servo 2 to specified position."""
        return self.set_servo(2, position, movement_time)
    
    def set_servo_3(self, position, movement_time=None):
        """Set servo 3 to specified position."""
        return self.set_servo(3, position, movement_time)
    
    def set_servo_4(self, position, movement_time=None):
        """Set servo 4 to specified position."""
        return self.set_servo(4, position, movement_time)
    
    def set_servo_5(self, position, movement_time=None):
        """Set servo 5 to specified position."""
        return self.set_servo(5, position, movement_time)
    
    def move_servo(self, servo_number, movement_amount, movement_time=None):
        """
        Move a specific servo by a relative amount from its current position.
        
        Args:
            servo_number (int): Servo number (1-5)
            movement_amount (int): Amount to move (positive or negative)
            movement_time (int, optional): Time for movement in milliseconds
        """
        if servo_number < 1 or servo_number > 5:
            print("Error: Servo number must be between 1 and 5")
            return False
        
        # Get current position
        current_position = self.servo_positions[servo_number - 1]
        
        # Calculate new position
        new_position = current_position + movement_amount
        
        min_position = 0
        max_position = 1800
        
        if new_position < min_position:
            print(f"Warning: New position {new_position} is below minimum {min_position}. Clamping to minimum.")
            new_position = min_position
        elif new_position > max_position:
            print(f"Warning: New position {new_position} is above maximum {max_position}. Clamping to maximum.")
            new_position = max_position
        
        print(f"Moving servo {servo_number} from {current_position} by {movement_amount} to {new_position}")
        
        # Use the existing set_servo function to move to the new position
        return self.set_servo(servo_number, new_position, movement_time)
    
    def set_all_servos(self, positions, movement_time=None):
        """
        Set all servos to specified positions.
        
        Args:
            positions (list): List of 5 positions for servos 1-5
            movement_time (int, optional): Time for movement in milliseconds
        """
        if len(positions) != 5:
            print("Error: Must provide exactly 5 positions")
            return False
            
        if movement_time is not None:
            self.timer = movement_time
            
        self.servo_positions = positions.copy()
        print(f"Setting all servos to positions: {positions}")
        
        return self._send_servo_data()
    
    def get_servo_position(self, servo_number):
        """Get the current position of a specific servo."""
        if servo_number < 1 or servo_number > 5:
            print("Error: Servo number must be between 1 and 5")
            return None
        return self.servo_positions[servo_number - 1]
    
    def get_all_positions(self):
        """Get current positions of all servos."""
        return self.servo_positions.copy()
    
    def reset_to_neutral(self, movement_time=1000):
        """Reset all servos to neutral position (900)."""
        neutral_positions = [900, 1200, 900, 900, 900]
        return self.set_all_servos(neutral_positions, movement_time)

# Example usage:
if __name__ == "__main__":
    # Create controller
    controller = ServoController()
    
    # Open connection
    if controller.open():
        print("Controller connected successfully!")
        
        # Example movements
        time.sleep(1)
        
        # Move individual servos
        controller.set_servo_1(1200)  # Move servo 1
        time.sleep(2)
        
        controller.set_servo_2(1500)  # Move servo 2
        time.sleep(2)
        
        # Move with custom timing
        controller.set_servo(3, 100, 2000)  # Servo 3, slow movement
        time.sleep(3)
        
        # Reset to neutral
        controller.reset_to_neutral()
        time.sleep(2)
        
        # Close connection
        controller.close()
    else:
        print("Failed to connect to controller.")
