#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import cv2
import time
import re
import AdapterBoard
from datetime import datetime

import live_roi_comp as lrc


## todo! ##
# we need to fix this part so that you can connect the leds
# you need to find out which gpio pins are still free and if we can use them
# the same way we would use pins 17, 18


GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

L1 = 33
L2 = 40

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)

def turn_on():
    GPIO.output(L1,1)
    GPIO.output(L2,0)

def turn_off():
    GPIO.output(L1,0)
    GPIO.output(L2,0)


def capture_imgs():
    ## accses camera and read current frameq
#     turn_on()
       
    ## get a timestamp for the file name
    t_str = time.ctime()
    time_search = re.search("([a-zA-Z]* *[0-9]*) ([0-9]{2}):([0-9]{2}):([0-9]{2})", t_str)
    
    now = datetime.now()

    ## TODO remove seconds
    curr_time = now.strftime("%m_%d__%H_%M_%S")
    print("Current Time =", curr_time)
    
#     date = time_search[1].replace("  ", "_") + "_"
#     hour = time_search[2]
#     minute = time_search[3]
#     sec = time_search[4]
#     curr_time = "_".join([date,hour,minute, sec])
    
    ## save the img
    cameras = AdapterBoard.MultiAdapter()

                    #(parent_path, f_name, width,height)
    my_path = "/home/pi/Desktop/agueda_imgs/__new_imgs__"
    cameras.save_imgs(my_path ,curr_time, 1280, 720)
    
#     cv2.imwrite("/home/pi/Desktop/agueda_imgs/imgs/{}.jpg".format(curr_time),frame)


## somthing like this to controll the correct light {"A", (40,33)}




#use this if you want a loop 
start = time.perf_counter()
print("starting loop-", time.ctime())
capture_imgs()

print("finished taking first img...\nwaiting for select ROI")
ROIs_dct = lrc.get_ROIs_for_all_cams(["A"])
# ROIs_dct = {'A': [(244, 300, 136, 191), (208, 289, 86, 145)], 'B': [(126, 133, 57, 38), (126, 118, 75, 70)], 'C': [(108, 118, 74, 57), (86, 118, 90, 69)], 'D': [(114, 123, 58, 47), (116, 122, 59, 53)]}
# real_start = start
while True:
#     if time.perf_counter()- real_start > 60:
#         break
    if time.perf_counter()- start > 240:
        start = time.perf_counter()
        capture_imgs()
        print("last img was taken at -", time.ctime())

        lrc.loop_through_cams(ROIs_dct)
        
#use this if youi want to use crontab
# capture_imgs()


