#!/usr/bin/env python3

import sys
import RPi.GPIO as GPIO
import matplotlib.path as mpltPath
from random import randint
import time
import os.path
from os import path
import inifilemodule
from math import sqrt
import servointerface

class Application:
    def __init__(self):
        
        self.GPIO_LASER = 27
        self.GPIO_BUZZER = 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_LASER,GPIO.OUT)
        GPIO.setup(self.GPIO_BUZZER,GPIO.OUT)

        self.points = []
        self.polygon = None

        self.mpltpoints= []
        self.mpltpoly = None

        self.x = []
        
        self.top = 0
        self.bottom = 0
        self.left = 0
        self.right = 0
        
        
        self.firstpoint = 0
        self.xdistance = 0
        self.ydistance = 0
        self.p1previous = (320,240)
        #self.playbuzzer()
        
        if __name__ == "__main__":
            self.calibration()

    def playbuzzer(self):
        time.sleep(.1)
        GPIO.output(self.GPIO_BUZZER,1)
        time.sleep(.05)
        GPIO.output(self.GPIO_BUZZER,0)
        time.sleep(.05)
        GPIO.output(self.GPIO_BUZZER,1)
        time.sleep(.05)
        GPIO.output(self.GPIO_BUZZER,0)
        time.sleep(.05)
        GPIO.output(self.GPIO_BUZZER,1)
        time.sleep(.05)
        GPIO.output(self.GPIO_BUZZER,0)
        
    def servouprotation(self,verticalpixel):
        uprotreq = (verticalpixel-35)*(int(self.bottom)-int(self.top))/(445-35)+int(self.top) #g(x)=(x-x1)*(y2-y1)/(x2-x1)+y1
        return uprotreq
        
    def servodownrotation(self,horizontalpixel):
        downrotreq = (horizontalpixel-35)*(int(self.right)-int(self.left))/(605-35)+int(self.left) #g(x)=(x-x1)*(y2-y1)/(x2-x1)+y1
        return downrotreq
    
    def carboxpattern(self, pstart, pend):
        
        distance = sqrt((pstart[0]-pend[0])**2+(pstart[1]-pend[1])**2)
        i=((pend[0]-pstart[0])/distance,(pend[1]-pstart[1])/distance)
        n=(i[1],-i[0])
        
        #1st point
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*i[1])
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*i[0])
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))               
        
        #2nd point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #3rd point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(3*i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(3*i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #4th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(3*i[1]-n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(3*i[0]-n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #5th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(5*i[1]-n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(5*i[0]-n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #6th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(5*i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(5*i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #7th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(7*i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(7*i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #8th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(7*i[1]-n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(7*i[0]-n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #9th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(9*i[1]-n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(9*i[0]-n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #10th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(9*i[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(9*i[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #pend
        uprotreq = self.servouprotation(pend[1])
        downrotreq = self.servodownrotation(pend[0])
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
    
    def diagonalpattern(self, pstart, pend):
        
        distance = sqrt((pstart[0]-pend[0])**2+(pstart[1]-pend[1])**2)
        i=((pend[0]-pstart[0])/distance,(pend[1]-pstart[1])/distance)
        n=(i[1],-i[0])

        #1st point
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))               
        
        #2nd point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(3*i[1]-n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(3*i[0]-n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #3rd point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(5*i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(5*i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #4th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(7*i[1]-n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(7*i[0]-n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #5th point 
        uprotreq = self.servouprotation(pstart[1]+0.1*distance*(9*i[1]+n[1]))
        downrotreq = self.servodownrotation(pstart[0]+0.1*distance*(9*i[0]+n[0]))
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
        #pend 
        uprotreq = self.servouprotation(pend[1])
        downrotreq = self.servodownrotation(pend[0])
        servointerface.pointservosdirect(int(uprotreq),int(downrotreq))
        
    
    def calibration(self):
        #check if an ini file is in the root folder.
        #If not, exit as calibration sequence requires camera
        if not path.isfile('/home/pi/AutoCatLaser/Catlaser.ini'):
            print ("No ini file, exiting")
            self.__del__()
            sys.exit()
        else:
            print ("Ini file found")
            self.top = inifilemodule.readcalibration()[0]
            self.bottom = inifilemodule.readcalibration()[1]
            self.left = inifilemodule.readcalibration()[2]
            self.right = inifilemodule.readcalibration()[3]
            
            self.points = inifilemodule.readpolygoninifile()
            self.mpltpoints = inifilemodule.readpathinifile()
            self.path = mpltPath.Path(self.mpltpoints)
            inifilemodule.writeinifile(self.points, self.mpltpoints)
            GPIO.output(self.GPIO_LASER,1)
            
            if __name__ == "__main__":
                self.playbuzzer()
                self.playmain()       

    def stop(self):
        GPIO.output(self.GPIO_LASER,0)

    def play(self):
        randpointx = randint(1,640)
        randpointy = randint(1,480)
        p1 = (randpointx,randpointy)

        inside2 = self.path.contains_point(p1)
        if inside2:
            pattern = randint(1,12)
                    
            if pattern ==1 or pattern ==2:
                self.carboxpattern(self.p1previous,p1)
            elif pattern ==3 or pattern ==4:
                self.diagonalpattern(self.p1previous, p1)
            else:
                uprotreq = self.servouprotation(randpointy)
                downrotreq = self.servodownrotation(randpointx)
                servointerface.pointservos(int(uprotreq),int(downrotreq))
                        
            self.p1previous = p1
                    
            randsleep = randint(1,4)
            if randsleep == 4:
                time.sleep(randint(10,30)/10.0)
                        
                        
    def playmain(self):
        try:
            while True:
                
                randpointx = randint(1,640)
                randpointy = randint(1,480)
                p1 = (randpointx,randpointy)

                inside2 = self.path.contains_point(p1)
                if inside2:
                    pattern = randint(1,12)
 
                    if pattern ==1 or pattern ==2:
                        self.carboxpattern(self.p1previous,p1)
                    elif pattern ==3 or pattern ==4:
                        self.diagonalpattern(self.p1previous, p1)
                    else:
                        uprotreq = self.servouprotation(randpointy)
                        downrotreq = self.servodownrotation(randpointx)
                        servointerface.pointservos(int(uprotreq),int(downrotreq))
                        
                    self.p1previous = p1

                    randsleep = randint(1,4)
                    if randsleep == 4:
                        time.sleep(randint(10,30)/10.0)
 
        except Exception as e:
            # swallowing exceptions isn't cool, but here we provide an opportunity to
            # print the exception to an output log, should crontab be configured this way
            # for debugging.
            print ('Unhandled exception: {0}'.format(str(e)))
                        
    def __del__(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.GPIO_LASER = 27
        self.GPIO_BUZZER = 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_LASER,GPIO.OUT)
        GPIO.setup(self.GPIO_BUZZER,GPIO.OUT)
        
        GPIO.output(self.GPIO_LASER,0)
        GPIO.output(self.GPIO_BUZZER,0)
        GPIO.cleanup()


# start the app
print("[INFO] starting...")
pba = Application()