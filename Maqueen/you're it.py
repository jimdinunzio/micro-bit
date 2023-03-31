# avoider.py
#
# Copyright (c) 2019 Jim DiNunzio MIT License

from microbit import *
import random

LOW_PWR = 25
#  MED_PWR = 60
HIGH_PWR = 80
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

def rotDegBlk(self, dir, deg):
    #  print("rot", deg, "degrees")
    maq.rot(dir, LOW_PWR)
    rotTimer = Timer(deg / DEG_PER_uSECOND)
    while not rotTimer.isTimeUp():
        sleep(20)
    maq.stop()

def fwdCmBlk(self, dist):
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


def rndPwr():
    return (random.random() / 2.0 + 0.4) * HIGH_PWR

# Main Routine
# initialize Hw and globals
maq = Robot()
random.seed(538)

while True:
    # Wait until game is started
    waitBtnAPress()
    sleep(2000)

    display.show(Image.HAPPY)
    # move straight, then pick a random direction, wait, then repeat
    move = 0

    # Main Playing Loop
    while True:
        if move == 0:
            maq.stop()
            sleep(random.randint(1000, 2000))

        elif move == 1:
            maq.fwd(HIGH_PWR)
            fwdTimer = Timer(random.randomint(15, 50) / CM_PER_uSECOND)
            while not fwdTimer.isTimeUp():
                dir, angle = chkBndry()
                if dir >= 0:
                    display.show(Image.SAD)
                    rotDegBlk(dir, angle)
                    fwdCmBlk(5)
                    break
                sleep(20)

        elif move == 2:
            slWhl = random.randint(LEFT, RIGHT)
            if slWhl == LEFT:
                lPwr = rndPwr()
                rPwr = HIGH_PWR
            else:
                lPwr = HIGH_PWR
                rPwr = rndPwr()
            maq.go(CW, CW, lPwr, rPwr)
            crvTimer = Timer(random.randomint(2000, 4000))
            while not crvTimer.isTimeUp():
                dir, angle = chkBndry()
                if dir >= 0:
                    display.show(Image.SAD)
                    rotDegBlk(dir, angle)
                    fwdCmBlk(5)
                    break
            sleep(20)
        sleep(5000)
        #  move = random.randint(0, 2)