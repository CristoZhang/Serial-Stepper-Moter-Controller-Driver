import serial
import time
from Mymodbus.Mymodbus import Mymodbus

ser = Mymodbus('COM3', 9600, timeout=1)

ser.set_speed(60)
ser.set_circle(8)
for i in range(2):
    ser.set_rotation(0)
    ser.start()
    ser.set_rotation(1)
    ser.start()

# print(ser.query_param(2))
ser.close()