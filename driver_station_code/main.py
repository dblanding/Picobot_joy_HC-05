# driver_station.py

from machine import ADC, Pin, UART
from time import sleep

uart = UART(0, 9600, timeout=100)
uart.write("Hello from HC-06\n")

x_joy = ADC(Pin(26))
y_joy = ADC(Pin(27))

while True:
    x_val = x_joy.read_u16()
    y_val = y_joy.read_u16()
    joy_vals = str(x_val) + ', ' + str(y_val)
    print(joy_vals)
    if uart.any() > 0:
        str_pose = uart.readline().decode().strip()
        try:
            str_x, str_y, str_rad = str_pose.split(',')
            x, y, rad = float(str_x), float(str_y), float(str_rad)
            pose = x, y, rad
            print(x, y, rad)
        except Exception as e:
            print(e)
            
        joy_vals += '\n'
        uart.write(joy_vals)
    
    sleep(0.1)