#!/usr/bin/env python3

import sys
from HeadlessLaser import Application
import datetime
import RPi.GPIO as GPIO
import time
from GmailWrapper import GmailWrapper
from imaplib import IMAP4
import logging

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')
 
HOSTNAME = 'YOUR EMAIL ADDRESS HOST (example: imap.gmail.com)'
USERNAME = 'YOUR EMAIL ADDRESS'
PASSWORD = 'YOUR EMAIL ADDRESS PASSWORD'

# seconds to wait before searching Gmail
CHECK_DELAY = 30

# seconds to wait before logging into gmail. if we don't wait, we run the risk of trying to 
# log in before the Pi had a chance to connect to wifi.
GMAIL_CONNECT_DELAY = 20
 
# minutes to wait before reconnecting our Gmail instance.
GMAIL_RECONNECT_DELAY = 60

GPIO_BUTTON = 26

FIRE_LASER_SUBJECT = 'start laser'
STOP_LASER_SUBJECT = 'stop laser'
 
HeadlessLaser = Application()
start_time = datetime.datetime.now()
runtime = 0
engage = False
gmailWrapper = None

defaultruntime = 180

last_gmail_check_time = datetime.datetime.now()
last_gmail_connect_attempt = datetime.datetime.now()
last_reconnect_attempt = datetime.datetime.now()

def StartLaser():
    global engage
    global gmailWrapper
    # setup the push button GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
 
    stop = False
    run = True
    engage = False
    checkcounter = 0
    # wire up a button press event handler to avoid missing a button click while the loop below
    # is busy processing something else.
    GPIO.add_event_detect(GPIO_BUTTON, GPIO.FALLING, callback=__button_handler, bouncetime=400)
    
    last_gmail_check = datetime.datetime.now().time()
    logging.info("running, press CTRL+C to exit...")
    
    try:
        while run:
            if checkcounter == 60:
                logging.info('30 minutes has passed since last log, still running.')
                checkcounter =0
                
            try:
                __check_gmail_connection()
                
                # avoid pinging gmail too frequently so they don't lock us out.
                if(__should_check_gmail(CHECK_DELAY)):
                    print ('Checking Gmail!')
                    stop = __should_stop_firing()
                    
                    ids = __get_email_ids_with_subject(FIRE_LASER_SUBJECT)
                    if(len(ids) > 0):
                        logging.info('Email found, initiating laser sequence!')
                        engage = True
            
                        HeadlessLaser.stop()
            
                        # grab any config options from the email and begin
                        #__calibrate_laser(__get_configuration(ids))
                        gmailWrapper.markAsRead(ids)
                        #print("ids=" , ids)
                        #__get_configuration(ids)
                        __calibrate_laser(__get_configuration(ids))
                        HeadlessLaser.calibration()
                        if not hasattr(HeadlessLaser,'path'):
                            print("no ini file, exit")
                            sys.exit()
                        HeadlessLaser.playbuzzer()
                    #else:
                        checkcounter+=1
                        print("No email found")
                
                if(stop):
                    engage = False
                    stop = False
                    HeadlessLaser.stop()
                    print ("stopping laser now")
                
                if(engage):
                    if(__runtime_elapsed()):
                        stop = True
                        logging.info('time ran out')
                    else:
                        HeadlessLaser.play()
                else:
                    # sleep here to lessen the CPU impact of our infinite loop
                    # while we're not busy shooting the laser. Without this, the CPU would
                    # be eaten up and potentially lock the Pi.
                    time.sleep(1)
                
            except IMAP4.abort as e:
                # Gmail will expire your session after a while, so when that happens we
                # need to reconect. Setting None here will trigger reconnect on the
                # next loop.
                gmailWrapper = None
                print ('IMAP4.abort exception: {0}'.format(str(e)))
            except Exception as e:
                # swallowing exceptions isn't cool, but here we provide an opportunity to
                # print the exception to an output log, should crontab be configured this way
                # for debugging.
                print ('Unhandled exception: {0}'.format(str(e)))
            except KeyboardInterrupt:
                run = False
                print ('KeyboardInterrupt: user quit the script.')
                break
    finally:
        #print ('Exiting program')
        HeadlessLaser.__del__()
 
def __button_handler(channel):
    global engage
    global firingtime
    
    logging.info('Button pressed! '.format(str(channel)))
    
    if(engage):
        now = datetime.datetime.now()
        end_time = (firingtime + datetime.timedelta(seconds=5)).time()
    
        if(now.time() > end_time):
            engage = False
            HeadlessLaser.stop()
            logging.info("button pressed, stopping the laser")
        else:
            logging.info('Already firing the laser, button press ignored for the next few seconds')
    else:
        logging.info('Initiating Laser')
        firingtime = datetime.datetime.now()
        # only start a new firing sequence if we're not already in the middle of one.
        engage = True
        __calibrate_laser(None)
        HeadlessLaser.calibration()
        if not hasattr(HeadlessLaser,'path'):
            print("no config file, exit")
            sys.exit()
        HeadlessLaser.playbuzzer()

def __check_gmail_connection():
    if(gmailWrapper is None):
        __connect_gmail()
    
def __connect_gmail():
    global gmailWrapper
    global last_gmail_connect_attempt
    
    now = datetime.datetime.now()
    next_connect_time = (last_gmail_connect_attempt + datetime.timedelta(seconds=GMAIL_CONNECT_DELAY)).time()
    if(now.time() > next_connect_time):
        logging.info('__connect_gmail: Attempting to login to Gmail')
        try:
            last_gmail_connect_attempt = now
            gmailWrapper = GmailWrapper(HOSTNAME, USERNAME, PASSWORD)
        except Exception as e:
            logging.info('__connect_gmail: Gmail failed during login, will retry automatically.'.format(str(e)))
 
def __should_check_gmail(delay):
    global last_gmail_check_time
    
    if(gmailWrapper is None):
        # we haven't yet successfully connected to Gmail, so exit
        return
    
    now = datetime.datetime.now()
    next_check_time = (last_gmail_check_time + datetime.timedelta(seconds=delay)).time()
    
    if(now.time() > next_check_time):
        last_gmail_check_time = now
        return True
    
    return False

def __runtime_elapsed():
    # figure out if the laser has ran its course, and should be stopped.
    now = datetime.datetime.now()
    end_time = (start_time + datetime.timedelta(seconds=runtime)).time()
    
    if(now.time() > end_time):
        return True
    
    return False
 
def __calibrate_laser(chosenruntime):
    global start_time
    global runtime
    
    if(chosenruntime is None):
        # no user defined config, so we'll go with the defaults
        runtime = defaultruntime
    else:
        runtime = chosenruntime
    logging.info("Laser playing for %i seconds" % runtime) 
    
    start_time = datetime.datetime.now()
    
    #runtime = configuration.get('runtime')
    
def __get_email_ids_with_subject(subject):
    return gmailWrapper.getIdsByGmailSearch('in:unread subject:{0}'.format(subject))
    
def __get_configuration(emailIds):
    subject = gmailWrapper.getFirstSubject(emailIds)
    config_start_index = subject.decode('utf8').find('(')
    # no config found in subject, so return nothing
    if(config_start_index == -1):
        return None
        
    else:
        # grab the substring from opening { to the end
        chosenruntime =subject.decode('utf8').partition("(")[2].partition(")")[0]
        if chosenruntime.isdigit():
            return int(chosenruntime)
        else:
            return None
 
def __should_stop_firing():
    ids = __get_email_ids_with_subject(STOP_LASER_SUBJECT)
    gmailWrapper.markAsRead(ids)
    return len(ids) > 0
 
if __name__ == '__main__':
    HeadlessLaser.playbuzzer()
    StartLaser()
