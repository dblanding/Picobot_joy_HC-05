# driver_station.py

from machine import ADC, Pin, UART
from time import sleep

uart = UART(0, 9600, timeout=100)
uart.write("Hello from HC-06\n")

xAxis = ADC(Pin(26))
yAxis = ADC(Pin(27))

while True:
    xRef = xAxis.read_u16()
    yRef = yAxis.read_u16()
    msg = str(xRef) + ', ' + str(yRef)
    if uart.any() > 0:
        str_pose = uart.readline().decode().strip()
        try:
            str_x, str_y, str_rad = str_pose.split(',')
            x, y, rad = float(str_x), float(str_y), float(str_rad)
            pose = x, y, rad
            print(x, y, rad)
        except Exception as e:
            print(e)
            
        msg = str(xRef) + ', ' + str(yRef)
        msg += '\n'
        uart.write(msg)
    
    sleep(0.2)