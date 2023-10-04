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
    print(msg)
    if uart.any() > 0:
        print(uart.readline())
        msg = str(xRef) + ', ' + str(yRef)
        msg += '\n'
        uart.write(msg)
    
    sleep(0.1)