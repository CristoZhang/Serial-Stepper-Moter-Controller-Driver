# Serial-Stepper-Moter-Controller-Driver
## 1. Overview
 This is a python based serial stepper motor controller driver library.  
  The specific models used are shown below：  
  ![image](https://github.com/WikChang/Serial-Stepper-Moter-Controller-Driver/blob/main/image/502d6c870e4adb04e1f16087e195345.jpg)  
  Taobao key words: 串口modbusRS485步进电机驱动器42/57/86控制可编程动作自动调速

 ---

## 2. Document
 This driver library is based on the **pyserial** and **time** library implementation.So please make sure that pyserial has finished according to it before using it.
 This library provides a class:**Mymodbus**, which inherits from **serial.Serial**.In addition to the methods inherited, the following methods have been added.

### 2.1 get_response()
 Reads a line of response and converts it to hex.

### 2.2 set_command()
 Set command to serial port.

### 2.3 query_param(function_code)
 Used to query the registers in the controller.The input parameters are integers **1 to 7**, corresponding to the following functions:
 | function_code | Function |
 | ----------- | ----------- |
 | 1 | Query rotation direction, 0001 for forward rotation, 0000 for reverse rotation. |
 | 2 | Query operation status, 0001 is running, 0000 is suspended or stopped. |
 | 3 | Query the preset speed in RPM. |
 | 4 | Query the preset pulse (if the pulse, circles and angle are **0**, then the working mode is permanent rotation.)|
 | 5 | Query the preset number of circles.|
 | 6 | Query the preset angle. |
 | 7 |Query the contents of each register of the preset. (?) I have not tried this instruction myself, if you have used it, please contact me to update it.|

 ### 2.4 set_rotation(function_code)
  Set the direction of rotation, **1** is forward, **0** is reverse.

 ### 2.5 set_speed(speed)
 Set the rotation speed, the value range is **0 to 1000**, in RPM.

 ### 2.6 set_impulse(impulse)
Set the number of pulses to run. If your stepper motor requires 1600 units of pulses for one revolution, then impulse is set to 1600 and will run for one revolution.
***Note that when initializing the job parameters, you only need to run one of set_impulse, set_circle, set_angle, which represent the different job states!***

### 2.7 set_circle(circles)
Set the number of circles to run, the range is **0~65535**.

### 2.8 set_angle(angle)
Set the angle to run, the range is **0~65535**.This may be affected by the stepping angle of the stepper motor, please refer to the parameters of the stepper motor.

### 2.9 start()
Start rotation.If the travel is zero (travel includes setting pulses, circle, angles), the motor will run for ten seconds and then stop.Timeout time of 10 seconds, Note that if the speed is too slow, be sure to add a delay or comment out the code related to timeout.

### 2.10 pasuse()
Pause rotation,If you pause and start again, the stepper motor will complete the previously unfinished tasks of the trip.

### 2.11 stop()
Stop rotation, This means complete interruption of the trip task.

---

## Summary
If you have questions about the above, please leave me a message or send me an email at cristozhang@stu.scau.edu.cn and I will respond at the first opportunity.