# driver_station (controller)
"""
Controller (this code) sends joystick values to robot.
Once the robot is turned on, it will respond to received values
by sending a comma-separated list of data (pose, distances, yaw).
The controller saves the data (transiently), then sends more joystick values.
To save the transient data to log a file, push the button.
"""

from machine import ADC, Pin, UART
import os
from time import sleep
import utime

# set up pins
led = Pin("LED", Pin.OUT)

uart = UART(0, 9600, timeout=100)
uart.write("Hello from HC-06\n")

x_joy = ADC(Pin(26))
y_joy = ADC(Pin(27))

button = Pin(18, Pin.IN, Pin.PULL_UP)

# flag signaling it's time to log data
LOG_DATA = False


def get_timestamp():
    now = utime.localtime()
    ts = (now[0], now[1], now[2], now[3], now[4], now[5]) 
    return "{:02d}-{:02d}-{:02d}_{:02d}-{:02d}-{:02d}".format(*ts)


def data_init():
    global datafile, f, prev_data
    datafile = "data.txt"
    f = open(datafile, 'w')
    prev_data = ''


def button_handler(pin):
    global LOG_DATA
    button.irq(handler=None)
    print(pin)
    LOG_DATA = True


def log_data():
    global LOG_DATA
    # move datafile to logfile
    f.close()
    filenames = os.listdir()
    logfilename = 'log' + get_timestamp() + '.txt'
    if datafile in filenames:
        os.rename(datafile, logfilename)
    
    LOG_DATA = False
    data_init()


button.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)
data_init()

while True:
    x_val = x_joy.read_u16()
    y_val = y_joy.read_u16()
    joy_vals = str(x_val) + ', ' + str(y_val)

    if uart.any() > 0:
        # normal data exchange with robot

        # read incoming data
        str_data = uart.readline().decode()
        print(str_data.rstrip())

        # write to datafile
        if not str_data == prev_data:
            prev_data = str_data
            f.write(str_data)
            f.flush()

        # Send joy_vals to robot
        joy_vals += '\n'
        uart.write(joy_vals)

    if LOG_DATA:
        log_data()

    led.toggle()
    sleep(0.1)
