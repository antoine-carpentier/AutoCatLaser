import configparser

config = configparser.ConfigParser()
config['CALIBRATION'] = {'Top': '90',
                     'Bottom': '90',
                     'Left': '90',
                     'Right': '90'}
config['POLYGON'] = {}
config['PATH'] = {}

   
def writeinifile(pointlist, mpltpoints):
    
    polygonlist = str(pointlist).strip('[]')
    pathlist= str(mpltpoints).strip('[]')
    
    config['POLYGON']['Points'] = polygonlist
    config['PATH']['Tuples'] = pathlist

    with open('/home/pi/AutoCatLaser/Catlaser.ini', 'w') as configfile:
        config.write(configfile)
        
def writecalibration(top, bottom, left, right):
    config['CALIBRATION']['Top'] = str(top)
    config['CALIBRATION']['Bottom'] = str(bottom)
    config['CALIBRATION']['Left'] = str(left)
    config['CALIBRATION']['Right'] = str(right)

    with open('/home/pi/AutoCatLaser/Catlaser.ini', 'w') as configfile:
        config.write(configfile)

def readcalibration():
    calib = []
    config.read('/home/pi/AutoCatLaser/Catlaser.ini')
    calib = [config['CALIBRATION']['Top'],config['CALIBRATION']['Bottom'],config['CALIBRATION']['Left'],config['CALIBRATION']['Right']]
    
    return calib

def readpolygoninifile():
    
    polygonlist = []
    
    config.read('/home/pi/AutoCatLaser/Catlaser.ini')
    polygonstring = config['POLYGON']['Points']
    polygonlist = [int(s) for s in polygonstring.split(',')]
    
    return polygonlist
    
def readpathinifile():
    
    pathlist = []
    
    config.read('/home/pi/AutoCatLaser/Catlaser.ini')
    pathstring = config['PATH']['Tuples']
    pathlist = [(el[0],el[-1]) for el in eval(pathstring)]

    return pathlist
    
    