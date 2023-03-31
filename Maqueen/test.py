from microbit import *
import urm10
#  import random

LOW_PWR = 30
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
DEG_PER_uSECOND = 360.0 / 1500.0
CM_PER_uSECOND = 24.0 / 1000.0


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
        self.go(CW, CW, pwr, pwr)
        self.status = FWD

    def stop(self):
        self.motor.stop(0)
        self.motor.stop(1)
        self.status = STP

    def rotateDegBlking(self, dir, deg):
        print("rotating ", deg, " degrees")
        self.rotate(dir, LOW_PWR)
        rotTimer = Timer(deg / DEG_PER_uSECOND)
        while not rotTimer.isTimeUp():
            pass
        self.stop()

    def fwdCmBlking(self, dist):
        print("forward ", dist, "cm")
        self.forward(MED_PWR)
        fwdTimer = Timer(dist / CM_PER_uSECOND)
        while not fwdTimer.isTimeUp():
            pass
        self.stop()

# globals
gState = READY
maq = None

def chkBndry():
    left = 0
    right = 0
    for i in range(5):
        left += pin13.read_digital()
        right += pin14.read_digital()
    left //= 5

    right //= 5
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

def waitUntilBtnAIsPressed():
    while True:
        if button_a.is_pressed():
            break

def checkQuitBtn():
    global gState
    if button_b.is_pressed():
        maq.stop()
        gState = READY

def getDist():
    return urm10.read(2, 1)

# Main Routine
# initialize Hw and globals
maq = MaqueenRobot()

while True:
    # Wait until game is started
    waitUntilBtnAIsPressed()
    sleep(2000)
    while True:
        dir, angle = chkBndry()
        if dir >= 0:
            display.show(Image.SAD)
        else:
            display.show(Image.HAPPY)
        sleep(20)
        checkQuitBtn()

def checkQuitBtn():
    global gState
    if button_b.is_pressed():
        maq.stop()
        gState = READY


        elif move == TURN:
            print("TURN")
            fRotDeg = rotDeg(random.randint(CW, CCW), random.randint(30, 90))
            while True:
                if not next(fRotDeg):
                    break
                dir, angle = chkBndry()
                if dir >= 0:
                    display.show(Image.SAD)
                    maq.rotDegBlk(dir, angle)
                    maq.fwdCmBlk(5)
                    break
            sleep(20)

            def rndPwr():
    return (random.random() / 2.0 + 0.4) * HIGH_PWR

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
                    maq.rotDegBlk(dir, angle)
                    maq.fwdCmBlk(5)
                    break
            sleep(20)
