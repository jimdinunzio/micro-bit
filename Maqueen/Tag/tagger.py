# tagger.py
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
MAX_OBJ_DIST = 91  # 2.54 * 12 * math.sqrt(3*3+3*3)

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

    def go(self, lDir, rDir, lPwr, rPwr):
        self.motor.run(LEFT, lDir, lPwr)
        self.motor.run(RIGHT, rDir, rPwr)

    def rot(self, dir, pwr):
        if dir == LEFT:
            lDir = CCW
            rDir = CW
        else:  # dir == RIGHT
            lDir = CW
            rDir = CCW
        self.go(lDir, rDir, pwr, pwr)

    def fwd(self, pwr):
        # music.stop()
        # print("going fwd")
        self.go(CW, CW, pwr, pwr)

    def stop(self):
        self.motor.stop(0)
        self.motor.stop(1)

    # Rotate deg degrees in dir (CW or CCW) direction
    # (blocking function - does not return until move is complete)
    def rotDegBlk(self, dir, deg):
        #  print("rot", deg, "degrees")
        self.rot(dir, LOW_PWR)
        rotTimer = Timer(deg / DEG_PER_uSECOND)
        while not rotTimer.isTimeUp():
            sleep(20)
        self.stop()

    # Go forward dist cm
    # (blocking function - does not return until move is complete)
    def fwdCmBlk(self, dist):
        #  print("Fwd", dist, "cm")
        self.fwd(HIGH_PWR)
        fwdTimer = Timer(dist / CM_PER_uSECOND)
        while not fwdTimer.isTimeUp():
            sleep(20)
        self.stop()

def waitBtnAPress():
    while True:
        if button_a.is_pressed():
            break

def getDist():
    return urm10.read(2, 1)

# globals
maq = None

# Rotate deg degrees at low power
# (python generator function) (non-blocking)
def rotDeg(dir, deg):
    maq.rot(dir, LOW_PWR)
    rotTimer = Timer(deg / DEG_PER_uSECOND)
    while True:
        if rotTimer.isTimeUp():
            maq.stop()
            yield False
        else:
            yield True

# Check whether robot has hit arena black boundary
# if hit, returns direction (CW or CCW) and angle to turn away from boundary
# if not hit, returns -1 for both dir and angle
def chkBndry():
    left = 0
    right = 0
    for i in range(5):
        left += pin13.read_digital()
        right += pin14.read_digital()
        sleep(3)
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
random.seed(538)

while True:
    # Wait until game is started
    waitBtnAPress()
    sleep(2000)
    rotCt = 0

    # Main Playing Loop
    while True:
        # Rotate in circle in random dir and find closest object
        # if hit boundary, turn away from it.
        # if rotated around 3 times and found nothing, go forward for 1 s and try again
        #  print("find obj")
        display.show(Image.HAPPY)
        if rotCt > 3:
            rotCt = 0
            maq.fwd(HIGH_PWR)
            fwdTimer = Timer(1000)
            while not fwdTimer.isTimeUp():
                dir, angle = chkBndry()
                if dir >= 0:
                    display.show(Image.SAD)
                    maq.rotDegBlk(dir, angle)
                    maq.fwdCmBlk(5)
                    break
                sleep(10)

        fRotDeg = rotDeg(random.randint(CW, CCW), 360)
        while True:
            if not next(fRotDeg):
                rotCt += 1
                break
            dist = getDist()
            if dist < MAX_OBJ_DIST:
                maq.stop()
                #  print("obj at ", dist, "cm")
                break
            dir, angle = chkBndry()
            if dir >= 0:
                display.show(Image.SAD)
                maq.rotDegBlk(dir, angle)
                maq.fwdCmBlk(5)
                break
            sleep(10)

        # if object found go in its direction that distance
        # if distance is getting bigger, then stop and search for object again
        if (dist < MAX_OBJ_DIST):
            display.show(Image.PACMAN)
            maq.fwd(HIGH_PWR)
            # allow time for acceleration
            sleep(100)
            while True:
                newDist = getDist()
                # print("dist=", newDist)
                if newDist > dist + 5:
                    break
                dist = newDist
                for i in range(1, 6):
                    dir, angle = chkBndry()
                    if dir >= 0:
                        display.show(Image.SAD)
                        maq.rotDegBlk(dir, angle)
                        maq.fwdCmBlk(5)
                        break
                if i < 5:
                    break