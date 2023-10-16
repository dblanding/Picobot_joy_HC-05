"""Demo for reading heading in UART-RVC mode.
Make sure pin P0 is pulled high to 3.3 V to enable UART-RVC
"""
from time import sleep
from machine import UART, Pin  # type: ignore
from bno08x_rvc import BNO08x_RVC, RVCReadTimeoutError

# STEMMA QT cable: Yellow -> tx; Blue -> rx
uart = UART(1, 115200, tx=Pin(4), rx=Pin(5))
rvc = BNO08x_RVC(uart)

try:
    while True:
        try:
            yaw, r, p, x, y, z = rvc.heading
            print(yaw)  # angle in degrees
        except RVCReadTimeoutError:
            print("Unable to read BNO08x UART.")
        sleep(.1)
except KeyboardInterrupt:
    print("\nCtrl-C pressed to exit.")
finally:
    uart.deinit()
