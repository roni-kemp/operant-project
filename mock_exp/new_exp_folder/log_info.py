import logging 
import datetime
import time

## check if you want to use this ^

## or this: 

    
import adafruit_dht
#from board import D20
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)

GPIO.setwarnings(False)

temp_high_pin = 36
GPIO.setup(temp_high_pin, GPIO.OUT)

## on
GPIO.output(temp_high_pin,1)
## off

# 
dht_device = adafruit_dht.DHT22(D20)

temperature = dht_device.temperature
humidity = dht_device.humidity
#humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)


# GPIO.output(temo_high_pin,0)
# 

#%%
def logg_info(temp, light_status, ROI_value):
    timestamp = datetime.datetime.now()
        
     
    info_timtemp = f"{timestamp} - Temperature: {temp}°C"
    info_exp = f"Light is: {light_status} - ROI: {ROI_value}"
        
    with open("info_log.txt", "a") as file:
        file.write(info_timtemp + "\n" +
        info_exp + "\n" )
            
logg_info('hola', 'laa', 'roi')            

#%%

if len(data)>5:
    logger.write(data)
    
    logger.write(32*"-"+"\n")
else:
    line = str(data) + "\n"
    logger.write(line)
