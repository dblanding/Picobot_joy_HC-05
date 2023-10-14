# driver_station.py

from machine import ADC, Pin, UART
import os
from time import sleep

uart = UART(0, 9600, timeout=100)
uart.write("Hello from HC-06\n")

x_joy = ADC(Pin(26))
y_joy = ADC(Pin(27))

# rotate logs and log previous data
filenames = os.listdir()
if 'log2.txt' in filenames:
    os.rename('log2.txt', 'log3.txt')
if 'log1.txt' in filenames:
    os.rename('log1.txt', 'log2.txt')
if 'log0.txt' in filenames:
    os.rename('log0.txt', 'log1.txt')
os.rename('data.txt', 'log0.txt')

# Start a new file for data
prev_data = ''
with open("data.txt", "w") as myfile:
            myfile.write(prev_data)
while True:
    x_val = x_joy.read_u16()
    y_val = y_joy.read_u16()
    joy_vals = str(x_val) + ', ' + str(y_val)
    # print(joy_vals)
    if uart.any() > 0:
        # read incoming data
        str_data = uart.readline().decode()
        print(str_data.rstrip())
        
        # append line of data to file
        if not str_data == prev_data:
            prev_data = str_data
            with open("data.txt", "a") as myfile:
                myfile.write(str_data)

        # Send joy_vals to robot
        joy_vals += '\n'
        uart.write(joy_vals)
    
    sleep(0.1)