# main.py

"""
MicroPython code for Pico car project using:
* Raspberry Pi Pico mounted on differential drive car
* 56:1 gear motors with encoders
* TeleOp control from driver station via HC-05 /06 BT 
* Odometer keeps track of pose (x, y, angle)
* Two VL53L0X devices measure left & right distance
* BNO08X IMU reports yaw w/r/t starting value (0)
* Send data (pose, l & r dist, yaw) back to controller
"""

import encoder_rp2 as encoder
import gc
import math
from machine import I2C, Pin, PWM, UART
from time import sleep
import motors
from odometer import Odometer
from parameters import TICKS_PER_METER, TARGET_TICK_RATE, TURN_SPD, ANGLE_TOL
from bno08x_rvc import BNO08x_RVC
import VL53L0X

# setup encoders
enc_b = encoder.Encoder(0, Pin(14))
enc_a = encoder.Encoder(1, Pin(12))

# setup onboard LED
led = machine.Pin("LED", machine.Pin.OUT)

# set up uart for BT communication
uart0 = UART(0, 9600, timeout=100)
uart0.write("Hello from HC-05\n")

# set up left & right VCSEL TOF distance sensors
def setup_tof_sensor(bus_id, sda_pin, scl_pin):
    """Setup a Vcsel sensor on an I2C bus.
    There are two available busses: 0 & 1.
    Return VL53L0X object."""
    sda = Pin(sda_pin)
    scl = Pin(scl_pin)

    print("setting up i2c%s" % bus_id)
    i2c = I2C(id=bus_id, sda=sda, scl=scl)
    print("Set up device %s on i2c%s" % (i2c.scan(), bus_id))

    return VL53L0X.VL53L0X(i2c)


tof0 = setup_tof_sensor(0, 8, 9)  # Left
tof0.start()
tof1 = setup_tof_sensor(1, 10, 11)  # Right
tof1.start()

# set up uart for IMU communication
uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart1.init(rxbuf=2048)
print(uart1)
rvc = BNO08x_RVC(uart1)
sleep(2) # wait for IMU to settle

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

    # get IMU data every time through loop
    try:
        yaw_degrees, *rest = rvc.heading
        # convert from degrees to radians
        yaw = yaw_degrees * math.pi / 180 
        if yaw != yaw_prev:
            yaw_prev = yaw
    except Exception as e:
        print(e)
        yaw = yaw_prev

    # slow loop
    if count == 0:
        count = N

        # read distances from sensors
        dist0 = tof0.read()
        dist1 = tof1.read()
        # print("left, right = ", dist0, dist1)

        if uart0.any() > 0:
            # get Bluetooth command
            linein = uart0.readline().decode().strip()

            # get latest encoder values
            enc_a_val = enc_a.value()
            enc_b_val = enc_b.value()

            # get current pose
            pose = odom.update(enc_a_val, enc_b_val)

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

            # send data to controller
            # This will signal request for next drive command
            pose_data = list(pose)
            dist_data = [dist0, dist1]
            data = pose_data + dist_data
            data.append(yaw)
            str_data = ', '.join(str(n) for n in data)
            uart0.write(str_data + "\n")

        led.toggle()

    count -= 1
    sleep(0.01)  # time delay for 'fast' loop (the IMU likes this speed)
