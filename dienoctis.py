import RPi.GPIO as GPIO
import time, datetime
import urllib
import json

#Sensor pins
PIR_PIN = 18
LICHT_PIN = 17
LED_PIN = 23

#Booleans voor de sensors
isLicht = 0     #wordt geupdate door de licht sensor
isZonOnder = 1  #wordt geupdate door de sunrise-sunset.org/api
isBeweging = 0  #wordt geupdate door de bewegings sensor

#globale variabelen
current_time_minute = 1
previious_time_minute = 0

#Initialisatie GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(LICHT_PIN,GPIO.IN,GPIO.PUD_DOWN)
GPIO.setup(PIR_PIN,GPIO.IN,GPIO.PUD_DOWN)
GPIO.setup(LED_PIN,GPIO.OUT)
previous_time_minute = 0
#Functions
def checkPIR():
    global current_time_minute
    global previous_time_minute
    global isBeweging

    current_movement = GPIO.input(PIR_PIN)
    current_time_minute = datetime.datetime.now().minute

    if current_movement:
        previous_time_minute = current_time_minute
        isBeweging = current_movement
        
    if previous_time_minute != current_time_minute :
        isBeweging = current_movement
        
    print "PIR checked"

def checkLICHT():
    global isLicht
    #controleer of er licht op de sensor valt
    isLicht = GPIO.input(LICHT_PIN)
    
    print "LICHT checked"

def checkAPI():
    #Format the system string
    global isZonOnder
    currentTime = datetime.datetime.now()

    #GET data from API
    response= urllib.urlopen("http://api.sunrise-sunset.org/json?lat=51.7201600&lng=-4.8203400&date=today")
    data = json.loads(response.read())
  
    #Format sunrise into datetime object
    sunriseData = data["results"]["sunrise"];
    sunriseDataSplit = sunriseData.split()
    sunriseTime = time.strptime(sunriseDataSplit[0], "%H:%M:%S")
    if sunriseDataSplit[1] == "PM":
        f = "2016-04-07 " + str(sunriseTime.tm_hour + 12) +":"+ str(sunriseTime.tm_min)+":" + str(sunriseTime.tm_sec) # create string
    else:
        f = "2016-04-07 " + str(sunriseTime.tm_hour) +":"+ str(sunriseTime.tm_min)+":" + str(sunriseTime.tm_sec) # create string
    sunriseTime = datetime.datetime.strptime(f,"%Y-%m-%d %H:%M:%S") #create object
    
    #Format sunset into datetime object
    sunsetData = data["results"]["sunset"];
    sunsetDataSplit = sunsetData.split()
     
    sunsetTime = time.strptime(sunsetDataSplit[0], "%H:%M:%S")
    if sunsetDataSplit[1] == "PM":
        f = "2016-04-05 " + str(sunsetTime.tm_hour + 12) +":"+ str(sunsetTime.tm_min)+":" + str(sunsetTime.tm_sec) # create string
    else:
        f = "2016-04-05 " + str(sunsetTime.tm_hour) +":"+ str(sunsetTime.tm_min)+":" + str(sunsetTime.tm_sec) # create string
    sunsetTime = datetime.datetime.strptime(f,"%Y-%m-%d %H:%M:%S") #create object

    #check if sun is up
    if(sunriseTime < currentTime and sunsetTime > currentTime):
        isZonOnder = 0
    else:
        isZonOnder = 1
    print sunriseTime
    print sunsetTime
    print currentTime
    print "API checked"

#main-loop
while True:
    checkPIR()
    checkLICHT()
    checkAPI()
    if not isLicht and isZonOnder and isBeweging:
        print("PIR status: %s" % (isBeweging))
        print("Licht sensor: %s" % (isLicht))
        print("API check %s") %(isZonOnder)
        GPIO.output(LED_PIN,GPIO.HIGH)
        print("lamp on")#turn on licht GPIO.set.....
    else:
        print("PIR status: %s" % (isBeweging))
        print("Licht sensor: %s" % (isLicht))
        print("API check %s") %(isZonOnder)
        GPIO.output(LED_PIN,GPIO.LOW)
        print("lamp off")#turn off licht
    print "-----------------cycle done------------\n\n"
    time.sleep(1)
