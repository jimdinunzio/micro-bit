# Obstacle Avoidance Program for the Micro:Maqueen robot based the micro:bit
# board
#
# This program starts driving the Maqueen robot 2s after pressing the A
# button straight until encountering an obstacle, then backs up to the right or
# left with warning beeping and then resumes going straight.  It stops after
# the set run time (RUN_TIME_MS) and can be run again by pressing the A button.
#
# This program was written in MIND+ (http://mindplus.cc/en.html)
# To upload it to the Maqueen, install MIND+ and copy code to the manual
# editing tab, connect to your robot and click Upload.  Have Fun!
#
# Copyright (c) 2019 Jim DiNunzio MIT License

from microbit import *
import music
import urm10
import random

# Adjust this to change the demonstration run time
RUN_TIME_MS = 10 * 1000

CW = 0
CCW = 1
LEFT_MOTOR = 0
RIGHT_MOTOR = 1
DIR_LEFT = 0
DIR_RIGHT = 1
DIR_STRAIGHT = 2
SLOW_SPEED = 30
MED_SPEED = 75
TOO_CLOSE = 8

class maqueen_motor:
    def __init__(self):
        self.I2C = i2c
        self.I2C.init(freq=100000, sda=pin20, scl=pin19)

    def run(self, motor, dir, speed):
        buf = bytearray(3)
        if motor == 0:
            buf[0] = 0x00
        else:
            buf[0] = 0x02
        buf[1] = dir
        buf[2] = speed
        self.I2C.write(0x10, buf)

    def stop(self, motor):
        self.run(motor, 0, 0)

class maqueen_robot:
    STOPPED = 0
    FORWARD = 1
    REVERSE = 2

    def __init__(self):
        self.motor = maqueen_motor()
        self.status = maqueen_robot.STOPPED

    def forward(self, speed):
        music.stop()
        self.motor.run(LEFT_MOTOR, CW, speed)
        self.motor.run(RIGHT_MOTOR, CW, speed)
        self.status = maqueen_robot.FORWARD

    def reverse(self, speed, turn):
        if turn == DIR_LEFT:
            rSpeed = speed // 2
            lSpeed = speed
        elif turn == DIR_RIGHT:
            rSpeed = speed
            lSpeed = speed // 2
        else:  # DIR_STRAIGHT
            rSpeed = speed
            lSpeed = speed

        self.motor.run(LEFT_MOTOR, CCW, lSpeed)
        self.motor.run(RIGHT_MOTOR, CCW, rSpeed)
        music.play(['B5:4', 'r:4'], pin=pin0, wait=False, loop=True)
        self.status = maqueen_robot.REVERSE

    def stop(self):
        self.motor.stop(0)
        self.motor.stop(1)
        music.stop()
        self.status = maqueen_robot.STOPPED

def onCheckTimeUp():
    endTime = running_time() + RUN_TIME_MS
    while True:
        value = running_time() - endTime
        yield value >= 0

maqueen = maqueen_robot()
func_CheckTimeUp = onCheckTimeUp()
random.seed(538)

while True:
    func_CheckTimeUp = onCheckTimeUp()
    while True:
        if button_a.is_pressed() and not button_b.is_pressed():
            break

    sleep(2000)
    while True:
        if next(func_CheckTimeUp):
            print("Times up!")
            maqueen.stop()
            break

        echo_distance = urm10.read(2, 1)
#        print("distance = ", echo_distance)
        if echo_distance <= TOO_CLOSE and maqueen.status != maqueen.REVERSE:
            print("Obstacle Detected, reversing and turning")
            dir = random.randint(DIR_LEFT, DIR_RIGHT)
            maqueen.reverse(SLOW_SPEED, dir)
            sleep(3000)
        elif maqueen.status != maqueen.FORWARD:
            print("Going Forward")
            maqueen.forward(MED_SPEED)