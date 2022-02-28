
from ctypes import *
import os
import faulthandler; faulthandler.enable()
import time
import threading
from random import randint
from math import sqrt

servofile = "/home/pi/AutoCatLaser/PCA9685_servo_driver.so"
servodriver=CDLL(servofile, mode = os.RTLD_LAZY)

ServoDownDegree = 90
ServoUpDegree = 90

SERVO_UP_CH = 0
SERVO_DOWN_CH =1

I2C_ADDR = 0x80 


servodriver.PCA9685_init.restype = None
servodriver.PCA9685_init.argtypes = [c_ubyte]

servodriver.PCA9685_setPWMFreq.restype = None
servodriver.PCA9685_setPWMFreq.argtypes = [c_float]

servodriver.PCA9685_init(0x80)
servodriver.PCA9685_setPWMFreq(60)


time.sleep(.5)

servodriver.setServoDegree.restype = None
servodriver.setServoDegree.argtypes = [c_ubyte,c_double]

servodriver.ServoDegreeDecrease.restype = c_int
servodriver.ServoDegreeDecrease.argtypes = [c_ubyte,c_double]

servodriver.ServoDegreeIncrease.restype = c_int
servodriver.ServoDegreeIncrease.argtypes = [c_ubyte,c_double]

def movecenter():
    global ServoDownDegree
    global ServoUpDegree
    
    if (90>ServoUpDegree):      
        moveup(abs(90-ServoUpDegree))
    else:
        movedown(abs(90-ServoUpDegree))
                
    if (90>ServoDownDegree):     
        moveright(abs(90-ServoDownDegree))
    else:
        moveleft(abs(90-ServoDownDegree))

def moveleft(STEP):
    global ServoDownDegree
    ServoDownDegree = ServoDownDegree - STEP 
    servodriver.ServoDegreeDecrease(SERVO_DOWN_CH, STEP)  
    
def moveright(STEP):
    global ServoDownDegree
    ServoDownDegree = ServoDownDegree + STEP
    servodriver.ServoDegreeIncrease(SERVO_DOWN_CH, STEP)
    
def movedown(STEP):
    global ServoUpDegree
    ServoUpDegree = ServoUpDegree - STEP 
    servodriver.ServoDegreeDecrease(SERVO_UP_CH, STEP)  
    
def moveup(STEP):
    global ServoUpDegree
    ServoUpDegree = ServoUpDegree + STEP
    servodriver.ServoDegreeIncrease(SERVO_UP_CH, STEP)
                   
def pointservos(uprotreq,downrotreq):
    global ServoUpDegree
    global ServoDownDegree
    
    delay = randint(10,25)/10.0
    upstep = abs(uprotreq-ServoUpDegree)/20
    downstep = abs(downrotreq-ServoDownDegree)/20
            
    for i in range (1,20):
        if (uprotreq>ServoUpDegree):      
            moveup(upstep)
        else:
            movedown(upstep)
                
        if (downrotreq>ServoDownDegree):     
            moveright(downstep)
        else:
            moveleft(downstep)
        
        sleeptime = sqrt(upstep**2+downstep**2)*delay*0.015
        time.sleep(sleeptime)
    
def pointservosdirect(uprotreq,downrotreq):
    global ServoUpDegree
    global ServoDownDegree
    
    delay = randint(10,25)/10.0
    upstep = abs(uprotreq-ServoUpDegree)/4
    downstep = abs(downrotreq-ServoDownDegree)/4
            
    for i in range (1,4):
        if (uprotreq>ServoUpDegree):      
            moveup(upstep)
        else:
            movedown(upstep)
                
        if (downrotreq>ServoDownDegree):     
            moveright(downstep)
        else:
            moveleft(downstep)
        
        sleeptime = sqrt(upstep**2+downstep**2)*delay*0.015
        time.sleep(sleeptime)