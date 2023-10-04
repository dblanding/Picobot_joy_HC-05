# main.py
# works with HC-06 TeleOp control

from machine import UART, Pin 
from time import sleep
import motors
from bno08x_rvc import BNO08x_RVC

led = machine.Pin("LED", machine.Pin.OUT)
"""
uart1 = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))  # IMU
uart1.init(rxbuf=2048)
print(uart1)
rvc = BNO08x_RVC(uart1)
sleep(2) # wait for IMU to settle
"""
uart0 = UART(0, 9600, timeout=100)  # BT comm
# sleep(1)
uart0.write("Hello from HC-05\n")

def joy_to_speed(joy_val):
    """
    Accept joystick value in range 0 to 65_535
    Convert to speed value in the range -1 to +1
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
N = 10  # get joystick data every Nth time through loop
count = N
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
    # get joystick values every Nth time through loop
    if count == 0:
        count = N
        if uart0.any() > 0:
            linein = uart0.readline().decode().strip()
            try:
                str_x, str_y = linein.split(',')
                x = int(str_x)
                y = int(str_y)
                lin_spd = joy_to_speed(y)
                ang_spd = joy_to_speed(x)
            except Exception as e:
                lin_spd, ang_spd = 0, 0
            print(lin_spd, ang_spd)
            # print(yaw)

            # send commands to motors
            motors.drive_motors(lin_spd, ang_spd)

            # send character to signal request for more data
            uart0.write("A\n")
            
        led.toggle()

    count -= 1
    sleep(0.01)  # this is the speed the IMU likes
