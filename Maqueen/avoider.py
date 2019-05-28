# avoider.py
#
# Copyright (c) 2019 Jim DiNunzio MIT License

from microbit import *
import urm10
import random

LOW_PWR = 25
#  MED_PWR = 60
HIGH_PWR = 100
CW = 0
CCW = 1
LEFT = 0
RIGHT = 1
DEG_PER_uSECOND = 0.24  # 360.0/1500.0
CM_PER_uSECOND = 0.024  # 24.0/1000.0
#  MAX_OBJ_DIST = 91  # 2.54 * 12 * math.sqrt(3*3+3*3)

class Motor:
    def __init__(self):
        self.I2C = i2c
        self.I2C.init(freq=100000, sda=pin20, scl=pin19)

    def run(self, motor, dir, pwrPnct):
        buf = bytearray(3)
        if motor == 0:
            buf[0] = 0x00
        else:
            buf[0] = 0x02
        buf[1] = dir
        buf[2] = (255 * pwrPnct + 50) // 100
        self.I2C.write(0x10, buf)

    def stop(self, motor):
        self.run(motor, 0, 0)

class Timer:
    def __init__(self, timeToWait):
        self.timeToWait = timeToWait
        self.endTime = running_time() + timeToWait

    def isTimeUp(self):
        return self.endTime - running_time() <= 0

class Robot:
    def __init__(self):
        self.motor = Motor()

    def rot(self, dir, pwr):
        if dir == LEFT:
            lDir = CCW
            rDir = CW
        else:  # dir == RIGHT
            lDir = CW
            rDir = CCW
        self.motor.run(LEFT, lDir, pwr)
        self.motor.run(RIGHT, rDir, pwr)

    def fwd(self, pwr):
        # music.stop()
        # print("going fwd")
        self.motor.run(LEFT, CW, pwr)
        self.motor.run(RIGHT, CW, pwr)

    def stop(self):
        self.motor.stop(0)
        self.motor.stop(1)

def rotDegBlk(dir, deg):
    #  print("rot", deg, "degrees")
    maq.rot(dir, LOW_PWR)
    rotTimer = Timer(deg / DEG_PER_uSECOND)
    while not rotTimer.isTimeUp():
        sleep(20)
    maq.stop()

def fwdCmBlk(dist):
    #  print("Fwd", dist, "cm")
    maq.fwd(HIGH_PWR)
    fwdTimer = Timer(dist / CM_PER_uSECOND)
    while not fwdTimer.isTimeUp():
        sleep(20)
    maq.stop()

def waitBtnAPress():
    while True:
        if button_a.is_pressed():
            break

def getDist():
    return urm10.read(2, 1)

# globals
maq = None

def rotDeg(dir, deg):
    maq.rot(dir, LOW_PWR)
    rotTimer = Timer(deg / DEG_PER_uSECOND)
    while True:
        if rotTimer.isTimeUp():
            maq.stop()
            yield False
        else:
            yield True

def chkBndry():
    left = 0
    right = 0
    for i in range(5):
        left += pin13.read_digital()
        right += pin14.read_digital()
        sleep(2)
    left = (left + 2.5) // 5
    right = (right + 2.5) // 5
    angle = 150
    dir = CW
    if right == 0 and left == 1:
        pass
    elif left == 0 and right == 1:
        dir = CCW
    elif right == 0 and left == 0:
        angle = 180
    else:
        return -1, -1
    return dir, angle

# Main Routine
# initialize Hw and globals
maq = Robot()
random.seed(892)

while True:
    # Wait until game is started
    waitBtnAPress()
    sleep(2000)
    # move straight, then pick a random direction, wait, then repeat
    mv = True
    avoid = False
    # Main Playing Loop
    while True:
        if avoid:
            avoid = False
        else:
            display.show(Image.HAPPY)
            pin8.write_digital(0)
            pin12.write_digital(0)
        if mv:
            maq.fwd(HIGH_PWR)
            fwdTimer = Timer(random.randint(25, 75) / CM_PER_uSECOND)
            while not fwdTimer.isTimeUp():
                d = urm10.read(2, 1)
                if d <= 15:
                    display.show(Image.SKULL)
                    pin8.write_digital(1)
                    pin12.write_digital(1)
                    avoid = True
                    break
                dir, angle = chkBndry()
                if dir >= 0:
                    display.show(Image.SAD)
                    rotDegBlk(dir, angle)
                    fwdCmBlk(5)
                    break
                sleep(10)
        else:
            fRotDeg = rotDeg(random.randint(CW, CCW), random.randint(30, 90))
            while True:
                if not next(fRotDeg):
                    break
                dir, angle = chkBndry()
                if dir >= 0:
                    display.show(Image.SAD)
                    rotDegBlk(dir, angle)
                    fwdCmBlk(5)
                    break
                sleep(10)
        mv = not mv