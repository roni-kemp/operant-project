## single cam
import RPi.GPIO as GPIO
import cv2
import re

import time
from datetime import datetime
import os
import numpy as np

import live_roi_comp as lrc

## set up pins to controll blue light
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

L1 = 12#33
L2 = 11#40

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)


def create_folder(path):
    ## Check if the folder exists
    ## Create empty folders if not
    if not os.path.isdir(path):
        os.makedirs(path)
        print("created folder")
    else:
        print("folder exists")


def save_imgs(parent_path, f_name, width, height):
    # init status
    was_ok = True
    
    ## handle folder path 
    directory_name = "B"
    path = os.path.join(parent_path, directory_name)
    
    create_folder(path)
    
    camera = cv2.VideoCapture(0)
    
    try:
        assert camera.isOpened()
        ret, frame = camera.read()
        
        if ret == True:
            file_path = path + "//" + f_name +".jpg"
            cv2.imwrite(file_path, frame)

        else:
            print(f"failed,{f_name} try again...")                    
#             my_logging((f_name, directory_name, "failed"))
            was_ok = False
                
    except AssertionError:
        print(f"{30*'#'}\n assertion error with video capture\n{30*'#'}")
        ## We should log this
        was_ok = False
        
    except:
        print("error when retrying...")
        was_ok = False
        ## We should log this
    # ADD finnaly?
    camera.release()
    return was_ok
    
def show(ROI_dct, path):
    """ 
    Meant to show a full img of the last capture with the ROIs highlighted
    """
    
    cv2.destroyAllWindows()

    ROIs = ROIs_dct["B"]
    for i in range(-1,1):
        img_path = os.listdir(path + "/B")[i]
        
        img = cv2.imread(path + f"/B/{img_path}")
        
        for i in range(2):#ROIs:
            ROI = ROIs[i]
            start_point = np.array((ROI[0]+i*int(img.shape[1]/2),ROI[1])) 
            end_point = start_point + np.array((ROI[2],ROI[3]))

            cv2.rectangle(img, start_point, end_point, (212, 220, 127), 3)

        img = cv2.resize(img,(int(img.shape[1]/2), int(img.shape[0]/2)))
        cv2.imshow(f"{img_path}",img)
        cv2.waitKey(10)

def capture_imgs(path):
    ## get a timestamp for the file name
    now = datetime.now()
    curr_time = now.strftime("%m_%d__%H_%M_%S")
    print("Current Time =", curr_time)
    
    ## loop and check if there was an error in capturing and saving the img
    ## if there was an error retry
    while True:
        was_ok = save_imgs(path ,curr_time, 1280, 720)
        if was_ok:
            break
        else:
            print("was not ok... retry...")
            time.sleep(2)
    print("was ok! NEXT!")


## def main():

## would like to swap this for a relative path in future
my_path = "/home/pi/Desktop/operant_testing"
time_between_imgs = 7

previous_pic_time = time.perf_counter()
print("starting run", time.ctime())

## Get the first img - used to choose the ROI
capture_imgs(my_path)
print("finished taking first img...\nwaiting for select ROI(!)")
ROIs_dct = lrc.get_ROIs_for_all_cams(my_path, ["B"])
light_dct = {"B_1":L1, "B_2":L2}
print(ROIs_dct)
## Allow the user to cancel the ROI selection
if ROIs_dct == None:
    exit()

## To start the loop imidiatly we tweak the previous_pic_time variable
previous_pic_time -= time_between_imgs

## Start the main loop this is the actual experiment
while True:
    ## Save the current the time
    curr_time = time.perf_counter()
    ## If more than X seconds past - take a picture, adjust lighting and update the last capture time
    if curr_time - previous_pic_time > time_between_imgs:
        capture_imgs(my_path)
        print("last img was taken at -", curr_time)
        lrc.loop_through_cams(ROIs_dct, light_dct, my_path)
        show(ROIs_dct, my_path)
        previous_pic_time = curr_time