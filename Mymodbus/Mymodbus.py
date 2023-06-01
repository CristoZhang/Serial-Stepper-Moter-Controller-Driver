import serial
import time

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
            time.sleep(0.05)   
        except serial.SerialException as e:
            print(f'Error writing to serial port: {e}')

    # Query modbus
    def query_param(self, function_code):
        # Validate the function code
        if function_code not in range(1, 8):
            raise ValueError('Invalid function code')

        # Define the query commands for each function code
        query_commands = {
            1: "01 03 00 01 00 01 D5 CA", #查询方向
            2: "01 03 00 02 00 01 25 CA", #查询状态
            3: "01 03 00 04 00 01 C5 CB", #查询速度
            4: "01 03 00 05 00 01 94 0B", #查询脉冲
            5: "01 03 00 06 00 01 64 0B", #查询圈数
            6: "01 03 00 07 00 01 35 CB", #查询角度
            7: "01 03 00 08 00 01 05 C8", #查询地址
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
            

    '''
    Start rotation
        If the travel is zero (travel includes setting pulses, circle, angles), 
        the guide will run for ten seconds and then stop.
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
            except IndexError:
                pass
            
            ''' Timeout time of 10 seconds,
            Note that if the speed is too slow, 
            be sure to add a delay or comment out the code.
            '''
            if time.time() - start_time > 10:  
                raise TimeoutError("Timeout while waiting for response")
                break

            if state is None:
                raise ValueError("State variable not initialized")
                break
            time.sleep(0.1)

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
    
    # Set the speed of the stepper motor, the unit is R/Min
    def set_speed(self, speed):
        if speed not in range(0, 1000): #1~1000R/Min
            raise ValueError('Invalid speed')
        speed = hex(speed)[2:].zfill(4)
        speed = speed[:2] +" "+ speed[2:]
        command = "01 06 00 04 " + speed + " C8 1A"
        self.set_command(command)

    '''
    The following three(set_impulse, set_circle,set_angle) 
    are the travel of the stepper motor, select one setting.
    '''
    # Set the number of pulses, the range is 0~65535
    def set_impulse(self, impulse):
        if impulse not in range(0, 65535):
            raise ValueError('Invalid impulse')
        impulse = hex(impulse)[2:].zfill(4)
        impulse = impulse[:2] +" "+ impulse[2:]
        command = "01 06 00 05 " + impulse + " 98 0D"
        self.set_command(command)
    
    # Set the number of circles, the range is 0~65535
    def set_circle(self, circle):
        if circle not in range(0, 65535):
            raise ValueError('Invalid circle')
        circle = hex(circle)[2:].zfill(4)
        circle = circle[:2] +" "+ circle[2:]
        command = "01 06 00 06 " + circle + " 68 0D"
        self.set_command(command)
    
    # Set the angle, the range is 0~65535
    def set_angle(self, angle):
        if angle not in range(0, 65535):
            raise ValueError('Invalid angle')
        angle = hex(angle)[2:].zfill(4)
        angle = angle[:2] +" "+ angle[2:]
        command = "01 06 00 07 " + angle + " 39 CD"
        self.set_command(command)

ser = Mymodbus('COM4', 9600, timeout=1)

ser.set_speed(120)
ser.set_circle(8)
for i in range(10):
    ser.set_rotation(0)
    ser.start()
    ser.set_rotation(1)
    ser.start()

ser.close()