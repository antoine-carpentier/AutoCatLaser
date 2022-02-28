#!/usr/bin/env python3

import RPi.GPIO as GPIO

from PIL import Image, ImageTk
import tkinter as tk

import matplotlib.path as mpltPath
from random import randint
import time
import os.path
from os import path
import inifilemodule
from pynput.mouse import Button, Controller
from math import sqrt
import cv2
import servointerface

class Application:
    def __init__(self):
        
        self.GPIO_LASER = 27
        self.GPIO_BUZZER = 24
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.GPIO_LASER,GPIO.OUT)
        GPIO.setup(self.GPIO_BUZZER,GPIO.OUT)
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.width = self.vs.get(cv2.CAP_PROP_FRAME_WIDTH ) #get the video's width
        self.height = self.vs.get(cv2.CAP_PROP_FRAME_HEIGHT ) #get the video's height
        self.root = tk.Tk()  # initialize root window
        self.root.title("AutoCatLaser")  # set window title
        self.root.geometry('%dx%d' % (self.width, self.height)) # set the window to the size of the camera feed
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.__del__)
        print(self.width, self.height)
        self.canvas = tk.Canvas(self.root)
        self.canvas.place(x=5, y=5, relwidth=1, relheight=1, width=-10, height=-10)
        
#         self.Entry1 = tk.Entry(self.canvas)
#         self.Entry2 = tk.Entry(self.canvas)
#         
#         self.Entry1.place(x=self.width/2-20, y=self.height/2-20, width=40, height=40)
        
        self.original = Image.open("/home/pi/AutoCatLaser/images/alien.png")
        self.image = ImageTk.PhotoImage(self.original)
        self.canvasimage=self.canvas.create_image(0, 0, image=self.image, anchor='nw', tags="IMG")
        
        self.Up=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/Up.png"))
        self.BigUp=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/BigUp.png"))
        self.Down=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/Down.png"))
        self.BigDown=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/BigDown.png"))
        self.Left=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/Left.png"))
        self.BigLeft=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/BigLeft.png"))
        self.Right=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/Right.png"))
        self.BigRight=ImageTk.PhotoImage(Image.open("/home/pi/AutoCatLaser/images/BigRight.png"))
        
        self.firstcircle = self.canvas.create_circle(35, 35, 15, outline='red', width=3)
        self.secondcircle = self.canvas.create_circle(605,445, 15, outline='red', width=3)
        
        self.canvas.itemconfigure(self.firstcircle, state='hidden')
        self.canvas.itemconfigure(self.secondcircle, state='hidden')
        
        self.UpArrowButton = tk.Button(self.canvas, image=self.Up, command = self.up)
        self.BigUpArrowButton = tk.Button(self.canvas, image=self.BigUp, command = self.bigup)

        self.DownArrowButton = tk.Button(self.canvas, image=self.Down, command = self.down)
        self.BigDownArrowButton = tk.Button(self.canvas, image=self.BigDown, command = self.bigdown)
        
        self.LeftArrowButton = tk.Button(self.canvas, image=self.Left, command = self.left)
        self.BigLeftArrowButton = tk.Button(self.canvas, image=self.BigLeft, command = self.bigleft)
     
        self.RightArrowButton = tk.Button(self.canvas, image=self.Right, command = self.right)
        self.BigRightArrowButton = tk.Button(self.canvas, image=self.BigRight, command = self.bigright)
        
        self.YesButton = tk.Button(self.canvas, text='YES',command = self.YesButtonPressed)
        self.NoButton = tk.Button(self.canvas, text='NO',command = self.NoButtonPressed)
           
        self.OKButton = tk.Button(self.canvas, text='OK',command = self.OKButtonPressed)
#         self.OKButton.place(x=self.width/2-20, y=self.height/2-20, width=40, height=40)
#         self.OKButton.place_forget()
        self.OKcounter = 0
        
        self.infotext=self.canvas.create_text(self.width/2,120, fill = 'white', font = "Cambria 12", text =  "Hello Laser",justify=tk.CENTER, anchor='center')
        self.canvas.itemconfigure(self.infotext, state='hidden')
        
#         self.canvas.bind('<Button-1>', self.click)
#         self.canvas.bind('<B1-Motion>', self.moveclick)
#         self.canvas.bind('<ButtonRelease-1>', self.release)
#         self.canvas.bind('<Button-2>', self.click2)

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()
        
        self.points = []
        self.polygon = None

        self.mpltpoints= []
        self.mpltpoly = None

        self.x = []
        
        self.top = 0
        self.bottom = 0
        self.left = 0
        self.right = 0
        
        print(inifilemodule.readcalibration()[1])
        
        self.calibration()
        
    def left(self):
        servointerface.moveleft(1)
        print(servointerface.ServoDownDegree)
    
    def bigleft(self):
        servointerface.moveleft(10)
        print(servointerface.ServoDownDegree)
        
    def right(self):
        servointerface.moveright(1)
        print(servointerface.ServoDownDegree)
    
    def bigright(self):
        servointerface.moveright(10)
        print(servointerface.ServoDownDegree)
        
    def up(self):
        servointerface.moveup(1)
        print(servointerface.ServoUpDegree)
    
    def bigup(self):
        servointerface.moveup(10)
        print(servointerface.ServoUpDegree)
        
    def down(self):
        servointerface.movedown(1)
        print(servointerface.ServoUpDegree)
    
    def bigdown(self):
        servointerface.movedown(10)
        print(servointerface.ServoUpDegree)
        
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


    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors 
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.canvas.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.canvas.itemconfig(self.canvasimage,image = imgtk)
        self.root.after(30, self.video_loop)  # call the same function after 30 milliseconds
        
    def video_refresh(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors 
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.canvas.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.canvas.itemconfig(self.canvasimage,image = imgtk)

    def calibration(self):
        #check if an ini file is in the root folder.
        #If not, launch calibration set up
        #if yes, ask if want to use quick game
        #if no quick game, launch drawing mode and replace polygon in ini file by new polygon
        if not path.isfile('Catlaser.ini'):
            self.canvas.itemconfigure(self.infotext, state='normal',text='As it is your first time using the toy, let\'s calibrate it')
            self.OKButton.place(x=self.width/2-20, y=self.height/2-20, width=40, height=40)
            #when press on ok, save servo rotations to ini file, then hide first circle, show second one
        else:
            self.top = inifilemodule.readcalibration()[0]
            self.bottom = inifilemodule.readcalibration()[1]
            self.left = inifilemodule.readcalibration()[2]
            self.right = inifilemodule.readcalibration()[3]
            
            self.canvas.itemconfigure(self.infotext, state='normal',text='Do you want to use the last-used play area?')
            self.YesButton.place(x=self.width/2-80, y=self.height/2-20, width=60, height=40)
            self.NoButton.place(x=self.width/2+20, y=self.height/2-20, width=60, height=40)    
    
    def servouprotation(self,verticalpixel):
        uprotreq = (verticalpixel-35)*(int(self.bottom)-int(self.top))/(445-35)+int(self.top) #g(x)=(x-x1)*(y2-y1)/(x2-x1)+y1
        return uprotreq
        
    def servodownrotation(self,horizontalpixel):
        downrotreq = (horizontalpixel-35)*(int(self.right)-int(self.left))/(605-35)+int(self.left) #g(x)=(x-x1)*(y2-y1)/(x2-x1)+y1
        return downrotreq        
    
    def OKButtonPressed(self):
        if self.OKcounter == 2:
            self.bottom = servointerface.ServoUpDegree
            self.right = servointerface.ServoDownDegree
            print('bot right corner')
            print(servointerface.ServoUpDegree, servointerface.ServoDownDegree)
            inifilemodule.writecalibration(self.top, self.bottom, self.left, self.right)
            
            
            self.canvas.itemconfigure(self.secondcircle, state='hidden')
            self.canvas.itemconfigure(self.infotext,text='Great! Now just draw the play area and press X when you are ready! \nYou can redraw the area if necessary')
            
            self.BigUpArrowButton.place_forget()
            self.UpArrowButton.place_forget()
            self.BigDownArrowButton.place_forget()
            self.DownArrowButton.place_forget()
            self.BigLeftArrowButton.place_forget()
            self.LeftArrowButton.place_forget()
            self.BigRightArrowButton.place_forget()
            self.RightArrowButton.place_forget()
            self.OKButton.place_forget()
            
            self.canvas.bind('<Button-1>', self.click)
            self.canvas.bind('<B1-Motion>', self.moveclick)
            self.canvas.bind('<ButtonRelease-1>', self.release)
            self.canvas.bind('<Button-2>', self.play)
            
        if self.OKcounter == 1:
            self.top = servointerface.ServoUpDegree
            self.left = servointerface.ServoDownDegree
            print('top left corner')
            print(servointerface.ServoUpDegree, servointerface.ServoDownDegree)

            servointerface.movecenter()
            
            servointerface.ServoUpDegree = 90
            servointerface.ServoDownDegree = 90
            
            self.canvas.itemconfigure(self.infotext,text='Now aim the laser in the bottom right circle and press OK')            
            self.canvas.itemconfigure(self.firstcircle, state='hidden')
            self.canvas.itemconfigure(self.secondcircle, state='normal')
            self.OKcounter = 2
            
        if self.OKcounter == 0:
            servointerface.movecenter()
            GPIO.output(self.GPIO_LASER,1)
            
            self.UpArrowButton.place(x=self.width/2-20, y=self.height/2-60, width=40, height=40)
            self.BigUpArrowButton.place(x=self.width/2-20, y=self.height/2-100, width=40, height=40)
            
            self.DownArrowButton.place(x=self.width/2-20, y=self.height/2+20, width=40, height=40)
            self.BigDownArrowButton.place(x=self.width/2-20, y=self.height/2+60, width=40, height=40)
            
            self.LeftArrowButton.place(x=self.width/2-60, y=self.height/2-20, width=40, height=40)
            self.BigLeftArrowButton.place(x=self.width/2-100, y=self.height/2-20, width=40, height=40)
            
            self.RightArrowButton.place(x=self.width/2+20, y=self.height/2-20, width=40, height=40)
            self.BigRightArrowButton.place(x=self.width/2+60, y=self.height/2-20, width=40, height=40)
            
            self.canvas.itemconfigure(self.firstcircle, state='normal')
            self.canvas.itemconfigure(self.infotext,text='Using the arrows, aim the laser in the top left circle and press OK')
            self.OKcounter = 1
               
    def YesButtonPressed(self):
        self.YesButton.place_forget()
        self.NoButton.place_forget()
        self.canvas.itemconfigure(self.infotext, state='hidden')
        
        self.points = inifilemodule.readpolygoninifile()
        self.mpltpoints = inifilemodule.readpathinifile()

        self.polygon = self.canvas.create_polygon(self.points, width=2, fill='red', outline='black', stipple = 'gray25')

        self.path = mpltPath.Path(self.mpltpoints)
        
        self.canvas.bind('<Button-1>', self.click)
        self.canvas.bind('<B1-Motion>', self.moveclick)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        self.canvas.bind('<Button-2>', self.play)
        
        Controller().click(Button.middle, 1)
      
    def NoButtonPressed(self):
        self.OKcounter = 2
        self.OKButtonPressed()
        self.YesButton.place_forget()
        self.NoButton.place_forget()
        
                       
    def click(self, event):
        # `coords()` needs flat list [x1, y1, x2, y2, ...] instead of [(x1, y1), (x2, y2), ...]
        # so I use `list.extend(other_list)` (`list += other_list`) instead of `list.append(other_list)
        self.mpltpoints.clear()
        self.points = [event.x, event.y]
        self.mpltpoints.append((event.x, event.y))
        print((event.x, event.y))
        print ([event.x, event.y])

        # at start there is no polygon on screen so there is nothing to delete
        if self.polygon:
            self.canvas.delete(self.polygon)
            self.polygon = None  # I need it in `move()`

        # `create_line()` needs at least two points so I cann't create it here.
        # I have to create it in `move()` when I will have two points

    def moveclick(self, event):
        # `coords()` needs flat list [x1, y1, x2, y2, ...] instead of [(x1, y1), (x2, y2), ...]
        # so I use `list.extend(other_list)` (`list += other_list`) instead of `list.append(other_list)
        self.points += [event.x, event.y]
        self.mpltpoints.append((event.x, event.y))

        if not self.polygon:
            # create line if not exists - now `self.points` have two points
            self.polygon = self.canvas.create_line(self.points, width=2)
        else:
            # update existing line
            self.canvas.coords(self.polygon, self.points)

    def release(self, event):
        # replace line with polygon to close it and fill it (BTW: `fill=""`if you want transparent polygon)
        self.canvas.delete(self.polygon)
        self.polygon = self.canvas.create_polygon(self.points, width=2, fill='red', outline='black', stipple = 'gray25')

        self.path = mpltPath.Path(self.mpltpoints)
                
        
    def play(self, event):
        inifilemodule.writeinifile(self.points, self.mpltpoints)
        GPIO.output(self.GPIO_LASER,1)  
        self.playbuzzer()
        
        self.canvas.itemconfigure(self.infotext, state='hidden')
        self.OKButton.place_forget()
        firstpoint = 0
        xdistance = 0
        ydistance = 0
        p1previous = (self.width/2,self.height/2)
        #for i in range(0,250):
        try:           
            while True:
                self.video_refresh()
                randpointx = randint(1,self.width)
                randpointy = randint(1,self.height)
                p1 = (randpointx,randpointy)

                inside2 = self.path.contains_point(p1)
                if inside2:

                    p1t = self.canvas.create_line(randpointx-5,randpointy-5,randpointx+5,randpointy+5,width=2)
                    p2t = self.canvas.create_line(randpointx+5,randpointy-5,randpointx-5,randpointy+5,width=2)
                    self.x.append(p1t)
                    self.x.append(p2t)

                    uprotreq = self.servouprotation(randpointy)
                    downrotreq = self.servodownrotation(randpointx)
                    
                    #print (uprotreq, downrotreq)

                    servointerface.pointservos(int(uprotreq),int(downrotreq))
                    
                    #print (servointerface.ServoUpDegree, servointerface.ServoDownDegree)
                    
                    xdistance=p1[0]-p1previous[0]
                    ydistance=p1[1]-p1previous[1]
                    diagdistance = sqrt(xdistance*xdistance+ydistance*ydistance)
                    #print(diagdistance)
                    
                    p1previous = p1

                    self.canvas.update_idletasks()
                    #time.sleep(randint(1,30)/10.0)
        except KeyboardInterrupt:
            pass
        self.__del__() 

    
    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle
    
    def __del__(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        GPIO.output(self.GPIO_LASER,0)
        GPIO.output(self.GPIO_BUZZER,0)
        GPIO.cleanup()
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application


# start the app
print("[INFO] starting...")
pba = Application()
pba.root.mainloop()