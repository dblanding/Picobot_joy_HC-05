# PicoBot TeleOperation using a pair of HC-05 / HC-06 BT modules.

* I did somthing like this with arduinos for driving the Omni-wheel car in teleOp mode.
    * The way it worked was to send motor speed values to the robot as comma separted (string) values
    * The robot would receive these string values, convert them to numerical values, then sendback a single character to acknowledge.
    * Once the acknowledgement message was received back, another comma separted string could is sent.

* The goal here is to do the same thing, except using picos instead of Arduinos
    * The driver station would use a 2 axis joystick (instead of 3)
    * The comma separated values would represent x and y joystick position (instead of 4 motor speeds)
        * Conversion from joystick value to motor speed would be done on the robot
* Here are the two Thonny sessions with both Picos communicating with each other:

![Two Thonny Sessions](imgs/thonny_sessions.png)

## Looks good! Now let's get 2 integer values representing joystick x, y

* Here's an article showing how to hook up the joystick: [Analog Joystick With Raspberry Pi Pico and MicroPython](https://peppe8o.com/analog-joystick-with-raspberry-pi-pico-and-micropython/)
* Excellent article, except for one thing... They show the joystick hooked up to 5V, then use 2 voltage dividers to bring the wiper voltage down to 3.3V. This introduces huge non-linearity because the impedance of the divider network is way too low for the 10K pots of the joystick.
    * Much better to hook the joystick up to 3.3V and then hook the pot wipers up directly to the A0 and A1 pins. No need for the 220 ohm resistors.

![Joystick wiring diagram](imgs/joystick-wiring-diagram.png)

### Here's the robot with HC-05 BT module and BNO08x IMU:

![Robot](imgs/picobot.jpg)

### And here's the controller: A cheapo 2-axis joystick attached to the top of the box it came in:

![Joystick Controller](imgs/controller.jpg)

### Inside the box is the Pico and HC-06 BT module:

![Inside Controller box](imgs/controller-open.jpg)

## Next, add Odometry: Use wheel encoder data to calculate current pose (x, y, angle)
* Starting from its **Home** position: pose = (0, 0, 0)
* PicoBot calculates its new updated pose = (x, y, angle) every time it receives a driving command
    * As acknowledgement of receipt of command, robot returns its current pose
