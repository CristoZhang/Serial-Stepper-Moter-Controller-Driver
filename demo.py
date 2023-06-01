import serial
import time
from Mymodbus.Mymodbus import Mymodbus

ser = Mymodbus('COM4', 9600, timeout=1)

ser.set_speed(120)
ser.set_circle(8)
for i in range(10):
    ser.set_rotation(0)
    ser.start()
    ser.set_rotation(1)
    ser.start()

ser.close()