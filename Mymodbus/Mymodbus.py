import serial
import time
import binascii

class Mymodbus(serial.Serial):
    def __init__(self, *args, **kwargs):
        super(Mymodbus, self).__init__(*args, **kwargs)

    # Get response from serial port
    def get_response(self):
        response = self.readline().hex()
        if response == '':
            return None  # Or other appropriate value
        else:
            return response

    # Set command to serial port
    def set_command(self,command):
        try:
            command = command.upper()
            # print(command)
            command = bytes.fromhex(command)
            self.flushInput()
            self.write(command)
            time.sleep(0.1)   
        except serial.SerialException as e:
            print(f'Error writing to serial port: {e}')

    # Calculate CRC16
    @staticmethod
    def crc16(data: bytes) -> bytes:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 1:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc.to_bytes(2, 'little')  # 'little' for little endian

    # Query modbus
    def query_param(self, function_code):
        # Validate the function code
        if function_code not in range(1, 8):
            raise ValueError('Invalid function code')

        # Define the query commands for each function code
        query_commands = {
            1: "01 03 00 01 00 01 D5 CA", #Query Direction
            2: "01 03 00 02 00 01 25 CA", #Query operation status
            3: "01 03 00 04 00 01 C5 CB", #Query speed
            4: "01 03 00 05 00 01 94 0B", #Query Pulse
            5: "01 03 00 06 00 01 64 0B", #Query the number of circles
            6: "01 03 00 07 00 01 35 CB", #Query Angle
            7: "01 03 00 08 00 01 05 C8", #Query Address
        }

        # Build the query based on the function code
        command = query_commands[function_code]
        # Write the query to the serial port
        self.set_command(command)
        # Read the response from the serial port
        response = self.get_response()
        if response is None:
            raise ValueError('Empty response')
        else:
            return response
    
    # Set rotation mode (0:reverse, 1:positive)
    def set_rotation(self, function_code):
        if function_code not in [0,1]:
            raise ValueError('Invalid function code')
        rotation_commands = {
            0:"01 06 00 01 00 00 D8 0A", #reverse
            1:"01 06 00 01 00 01 19 CA" #positive
        }
        command = rotation_commands[function_code]
        self.set_command(command)
            
    # Set the speed of the stepper motor, the unit is R/Min
    def set_speed(self, speed):
        if speed not in range(0, 1000): #1~1000R/Min
            raise ValueError('Invalid speed')
        # Create command without CRC
        command_without_crc = bytearray([0x01, 0x06, 0x00, 0x04, (speed >> 8) & 0xFF, speed & 0xFF])
        # Calculate CRC
        crc = self.crc16(command_without_crc)
        # Concatenate command with CRC
        command = command_without_crc + crc
        # Convert to hex string for printing
        command_str = ' '.join(f'{b:02X}' for b in command)
        self.set_command(command_str)

    '''
    The following three(set_impulse, set_circle,set_angle) 
    are the travel of the stepper motor, select one setting.
    '''
    # Set the number of pulses, the range is 0~65535
    def set_impulse(self, impulse):
        if impulse not in range(0, 65536):
            raise ValueError('Invalid impulse')
        command_without_crc = bytearray([0x01, 0x06, 0x00, 0x05, (impulse >> 8) & 0xFF, impulse & 0xFF])
        crc = self.crc16(command_without_crc)
        command = command_without_crc + crc
        command_str = ' '.join(f'{b:02X}' for b in command)
        self.set_command(command_str)
    
    # # Set the number of circles, the range is 0~65535
    def set_circle(self, circle):
        if circle not in range(0, 65536):
            raise ValueError('Invalid circle')
        command_without_crc = bytearray([0x01, 0x06, 0x00, 0x06, (circle >> 8) & 0xFF, circle & 0xFF])
        crc = self.crc16(command_without_crc)
        command = command_without_crc + crc
        command_str = ' '.join(f'{b:02X}' for b in command)
        self.set_command(command_str)
    
    # Set the angle, the range is 0~65535
    def set_angle(self, angle):
        if angle not in range(0, 65536):
            raise ValueError('Invalid angle')
        command_without_crc = bytearray([0x01, 0x06, 0x00, 0x07, (angle >> 8) & 0xFF, angle & 0xFF])
        crc = self.crc16(command_without_crc)
        command = command_without_crc + crc
        command_str = ' '.join(f'{b:02X}' for b in command)
        self.set_command(command_str)

    '''
    Start rotation
        If the travel is zero (travel includes setting pulses, circle, angles), 
        the motor will run for ten seconds and then stop.
    '''
    def start(self):
        self.set_command("01 06 00 02 00 01 E9 CA")
        start_time = time.time()
        state = None  # Initialize the state variable
        while True:
            try:
                data = self.query_param(2)
                # data = self.readline().hex()
                if len(data) >= 10:
                    state = data[6:10]
                # print(state)
                # print(data)
                if state != "0001":
                    break
            except ValueError as e:
                self.stop()
                pass
            
            ''' Timeout time of 10 seconds,
            Note that if the speed is too slow, 
            be sure to add a delay or comment out the code.
            '''
            if time.time() - start_time > 30:  
                raise TimeoutError("Timeout while waiting for response")
                break

            if state is None:
                raise ValueError("State variable not initialized")
                break
            time.sleep(0.05)

    '''Pause rotation
    If you pause and start again, 
    the stepper motor will complete the previously unfinished tasks of the trip.
    '''
    def pause(self):
        self.set_command("01 06 00 02 00 00 28 0A")
    
    '''Stop rotation
    This means complete interruption of the trip task.
    '''
    def stop(self):
        self.set_command("01 06 00 03 00 01 B8 0A")
