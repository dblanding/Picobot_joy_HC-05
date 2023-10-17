# driver_station (controller)
"""
Controller (this code) sends joystick values to robot.
It will wait patiently until robot is turned on.

Once it is turned on, the robot will respond to received values
by sending a comma-separated list of data (pose, dist, yaw).

The controller saves the data, then sends more joystick values.

This continues as long as the robot is powered.

To save the data to file, turn the robot off.
Once the robot is switched off, the controller will wait 2s,
then rotate the logs and store current data as log0.txt
"""

from machine import ADC, Pin, UART
import os
from time import sleep

uart = UART(0, 9600, timeout=100)
uart.write("Hello from HC-06\n")

x_joy = ADC(Pin(26))
y_joy = ADC(Pin(27))

def rotate_logs():
    # rotate logs and log current data
    filenames = os.listdir()
    print(filenames)
    if 'log1.txt' in filenames:
        os.rename('log1.txt', 'log2.txt')
    if 'log0.txt' in filenames:
        os.rename('log0.txt', 'log1.txt')
    with open('log0.txt', 'w') as f:
        for line in datalist:
            f.write(line)

# Create a list for data
datalist = []
prev_data = ''

# initial values associated with saving & logging data

LOG_WAIT_COUNT = 20  # Trigger logging after 2s nonresponse from robot
robot_alive = False
logs_rotated = True
wait_counter = 0

while True:
    x_val = x_joy.read_u16()
    y_val = y_joy.read_u16()
    joy_vals = str(x_val) + ', ' + str(y_val)
    # print(joy_vals)

    if uart.any() > 0:
        # normal data exchange with robot (until robot is turned off)
        robot_alive = True
        logs_rotated = False
        # read incoming data
        str_data = uart.readline().decode()
        print(str_data.rstrip())

        # append line of data to file
        if not str_data == prev_data:
            prev_data = str_data
            datalist.append(str_data)

        # Send joy_vals to robot
        joy_vals += '\n'
        uart.write(joy_vals)

    elif robot_alive:
        # start counter when no data received from robot
        wait_counter = 0
        robot_alive = False
        print("robot_alive")

    elif wait_counter == LOG_WAIT_COUNT:
        # Time's up! Log data and rotate logs.
        rotate_logs()
        logs_rotated = True
        wait_counter = 0
        print("logs rotated")

    elif not logs_rotated:
        # increment counter (keep waiting)
        wait_counter += 1
        print("wait_counter = ", wait_counter)

    else:
        print("waiting")

    sleep(0.1)