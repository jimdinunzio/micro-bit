import necir

# Call backs from hardware

necir.init(16, IR_callback)

# Elegoo Remote
class Rem:
    UP = 47430
    DOWN = 59925
    LEFT = 47940
    RIGHT = 48195
    OK = 48960
    ONE = 59670
    TWO = 58905


# Handle IR
def IR_callback(IR_addr, IR_cmd):
    global gState
    print("IR Cmd : ", IR_cmd)
    if IR_cmd == Rem.OK:
        maq.stop()
        gState = READY
    elif IR_cmd == Rem.ONE:
        gState = PLAYING

            # Main Playing Loop
#    while True:
#        echo_distance = getEchoDistance()
#        # print("distance = ", echo_distance)
#        if echo_distance <= TOO_CLOSE and maq.status != REV:
#            print("Obstacle Detected, reversing and turning")
#            dir = random.randint(LEFT, RIGHT)
#            maq.reverse(LOW_PWR, dir)
#            sleep(1000)
#        elif maq.status != FWD:
#            print("Going Forward")
#            maq.forward(MED_PWR)
#        if gState == READY:
#            break

CM_PER_uSECOND = 20.0 / 1000.0

def fwdCm(cm):
    maq.forward(MED_PWR)
    fwdTimer = Timer(dist / CM_PER_uSECOND)
    while True:
        if fwdTimer.isTimeUp():
            maq.stop()
            yield False
        else:
            yield True

    def reverse(self, pwr, turn):
        if turn == LEFT:
            rPwr = (pwr + 1) // 2
            lPwr = pwr
        elif turn == RIGHT:
            rPwr = pwr
            lPwr = (pwr + 1) // 2
        else:  # STRAIGHT
            rPwr = pwr
            lPwr = pwr

        self.go(CCW, CCW, lPwr, rPwr)
        # music.play(['B5:4', 'r:4'], pin=pin0, wait=False, loop=True)
        self.status = REV

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

def setLights(color):
    np = neopixel.NeoPixel(pin15, 4)
    for i in range(4):
        np[i] = color
    np.show()