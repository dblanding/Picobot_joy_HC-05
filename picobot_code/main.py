# main.py

"""
MicroPython code for Pico car project using:
* Raspberry Pi Pico mounted on differential drive car
* 56:1 gear motors with encoders
* TeleOp control from driver station via HC-05 /06 BT 
* Odometer keeps track of pose (x, y, angle)
* Sends pose data back to driver station
"""

import encoder_rp2 as encoder
import gc
import math
from machine import UART, Pin, PWM 
from time import sleep
import motors
from odometer import Odometer
from parameters import TICKS_PER_METER, TARGET_TICK_RATE, TURN_SPD, ANGLE_TOL
from bno08x_rvc import BNO08x_RVC

# setup encoders
enc_b = encoder.Encoder(0, Pin(14))
enc_a = encoder.Encoder(1, Pin(12))

# setup onboard LED
led = machine.Pin("LED", machine.Pin.OUT)

# set up uart for BT communication
uart0 = UART(0, 9600, timeout=100)
uart0.write("Hello from HC-05\n")

"""
# set up uart for IMU communication
uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart1.init(rxbuf=2048)
print(uart1)
rvc = BNO08x_RVC(uart1)
sleep(2) # wait for IMU to settle
"""

def joy_to_speed(joy_val):
    """
    Accept joystick value in range 0 to 65_535
    Convert to (and return) speed value in the range -1 to +1
    """
    joy_min = 0
    joy_max = 65_535
    joy_range = joy_max - joy_min
    spd_min = -1
    spd_max = 1
    spd_range = spd_max - spd_min
    
    spd = ((joy_val - joy_min) * spd_range) / joy_range + spd_min
    if abs(spd) < 0.1:
        spd = 0
    return spd

yaw_prev = 0
N = 10  # number of 'fast' loop cycles per 'slow' loop
count = N
odom = Odometer()
while True:
    """
    # get IMU data every time through loop
    try:
        yaw, *rest = rvc.heading
        if yaw != yaw_prev:
            yaw_prev = yaw
    except Exception as e:
        print(e)
        yaw = yaw_prev
    """
    # slow loop
    if count == 0:
        count = N
        if uart0.any() > 0:
            # get Bluetooth command
            linein = uart0.readline().decode().strip()

            # get latest encoder values
            enc_a_val = enc_a.value()
            enc_b_val = enc_b.value()

            # get current pose
            pose = odom.update(enc_a_val, enc_b_val)
            # pose_x, pose_y, pose_angle = pose
            # pose_ang_deg = pose_angle * 180 / math.pi
            # pose_deg = (pose_x, pose_y, pose_ang_deg)  # for display
            
            # process BT command
            try:
                str_x, str_y = linein.split(',')
                x = int(str_x)
                y = int(str_y)
                lin_spd = joy_to_speed(y)
                ang_spd = joy_to_speed(x)
            except Exception as e:
                lin_spd, ang_spd = 0, 0
            # print(lin_spd, ang_spd)

            # send commands to motors
            motors.drive_motors(lin_spd, ang_spd)

            # send pose data to signal request for next drive command
            str_pose = ', '.join(str(n) for n in pose)
            uart0.write(str_pose + "\n")
            
        led.toggle()

    count -= 1
    sleep(0.01)  # time delay for 'fast' loop (the IMU likes this speed)
