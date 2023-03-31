# tagger.py
#
# Copyright (c) 2019 Jim DiNunzio MIT License

from microbit import *
import urm10
import random

LOW_PWR = 25
MED_PWR = 60
HIGH_PWR = 80
CW = 0
CCW = 1
LEFT = 0
RIGHT = 1
READY = 0
PLAYING = 1
STP = 0
FWD = 1
REV = 2
DEG_PER_uSECOND = 0.24  # 360.0/1500.0
CM_PER_uSECOND = 0.024  # 24.0/1000.0
MAX_OBJ_DIST = 86  # 2.54 * 12 * math.sqrt(3*3+3*3)

class MaqueenMotor:
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

    def timeLeft(self):
        return self.endTime - running_time()

    def isTimeUp(self):
        return self.timeLeft() <= 0

class MaqueenRobot:
    def __init__(self):
        self.motor = MaqueenMotor()
        self.status = STP

    def go(self, lDir, rDir, lPwr, rPwr):
        self.motor.run(LEFT, lDir, lPwr)
        self.motor.run(RIGHT, rDir, rPwr)

    def rotate(self, dir, pwr):
        if dir == LEFT:
            lDir = CCW
            rDir = CW
        else:  # dir == RIGHT
            lDir = CW
            rDir = CCW
        self.go(lDir, rDir, pwr, pwr)

    def forward(self, pwr):
        # music.stop()
        # print("going forward")
        self.go(CW, CW, pwr, pwr)
        self.status = FWD

    def stop(self):
        self.motor.stop(0)
        self.motor.stop(1)
        self.status = STP

    def rotateDegBlking(self, dir, deg):
        #  print("rot", deg, "degrees")
        self.rotate(dir, LOW_PWR)
        rotTimer = Timer(deg / DEG_PER_uSECOND)
        while not rotTimer.isTimeUp():
            sleep(20)
        self.stop()

    def fwdCmBlking(self, dist):
        #  print("Fwd", dist, "cm")
        self.forward(HIGH_PWR)
        fwdTimer = Timer(dist / CM_PER_uSECOND)
        while not fwdTimer.isTimeUp():
            sleep(20)
        self.stop()

def waitUntilBtnAIsPressed():
    while True:
        if button_a.is_pressed():
            break

def getDist():
    return urm10.read(2, 1)

# globals
gState = READY
maq = None

def rotateDeg(dir, deg):
    maq.rotate(dir, LOW_PWR)
    rotTimer = Timer(deg / DEG_PER_uSECOND)
    while True:
        if rotTimer.isTimeUp():
            maq.stop()
            yield False
        else:
            yield True

def checkBoundary():
    left = pin13.read_digital()
    right = pin14.read_digital()
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

def avoidBoundary():
    dir, angle = checkBoundary()
    if dir >= 0:
        display.show(Image.SAD)
        maq.rotateDegBlking(dir, angle)
        maq.fwdCmBlking(5)
        return True
    return False

# Main Routine
# initialize Hw and globals
maq = MaqueenRobot()
random.seed(538)

while True:
    # Wait until game is started
    waitUntilBtnAIsPressed()
    sleep(2000)
    gState = PLAYING
    rotCount = 0

    # Main Playing Loop
    while gState == PLAYING:
        # Rotate in random dir find closest object
        #  print("find obj")
        display.show(Image.HAPPY)
        if rotCount > 2:  # if nothing found, move forward some
            goDist = random.randint(10,20)

        fRotateDeg = rotateDeg(random.randint(CW, CCW), 360)
        while True:
            if not next(fRotateDeg):
                ++rotCount
                break
            dist = getDist()
            if dist < MAX_OBJ_DIST:
                rotCount = 0
                maq.stop()
#                print("obj at ", dist, "cm")
                break
            if avoidBoundary()
                break

        # if object found go in its direction that distance
        # if distance is not closing anymore, then reaquire object
        if (dist < MAX_OBJ_DIST):
            display.show(Image.PACMAN)
            maq.forward(HIGH_PWR)
            # allow time for acceleration
            sleep(300)
            while True:
                newDist = getDist()
                # print("dist=", newDist)
                if newDist <= 2:
                    display.show(Image.SKULL)
                    maq.stop()
                    gState = READY
                    break
                if newDist > dist:
                    break
                dist = newDist
                for i in range(1, 6):
                    if avoidBoundary():
                        break
                    sleep(10)
                if i < 5:
                    break