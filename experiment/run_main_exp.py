## single cam
import RPi.GPIO as GPIO
import cv2
from picamera2 import Picamera2
from libcamera import controls

import time
from datetime import datetime
import os
import numpy as np

import live_roi_comp25 as lrc

def create_folder(path):
    ## Check if the folder exists and create empty folders if not
    if not os.path.isdir(path):
        
        os.makedirs(path)
        print("created folder")
    else:
        print("folder exists")


def save_imgs(parent_path, f_name, width, height):
    # init status
    was_ok = True
    
    ## handle folder path 
    directory_name = "imgs"
    path = os.path.join(parent_path, directory_name)
    
    create_folder(path)
    
    try:
        frame = picam2.capture_array("main")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        scale_percent = 30 # [%]
        width = int(frame.shape[1] * scale_percent / 100)
        height = int(frame.shape[0] * scale_percent / 100)
        dim = (width, height)
        frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        
        file_path = path + "//" + f_name +".jpg"
        cv2.imwrite(file_path, frame)
                
    except AssertionError:
        print(f"{30*'#'}\n assertion error with video capture\n{30*'#'}")
        ## We should log this
        was_ok = False
        
    except:
        print("error when retrying...")
        was_ok = False
        ## We should log this
    # ADD finnaly?
    #camera.release()
    return was_ok


def show(ROIs_dct, path):
    """ 
    Meant to show a full img of the last capture with the ROIs highlighted
    """
    ## clean up old windows, and open new one
    #cv2.destroyAllWindows()
    cv2.namedWindow("first and last imgs", cv2.WINDOW_NORMAL)
    
    ROIs = ROIs_dct["B"]
    
    img_lst = []
    ## Show the first and last img (-1, 0)
    for i in range(-1,1):
        img_path = sorted(os.listdir(path + "/B"))[i]
        img = cv2.imread(path + f"/B/{img_path}")
        
        for i in range(2):#ROIs:
            ROI = ROIs[i]
            start_point = np.array((ROI[0]+i*int(img.shape[1]/2),ROI[1])) 
            end_point = start_point + np.array((ROI[2],ROI[3]))
            
            rect_color = (212, 220-(100*i), 127+(100*i))
            
            cv2.rectangle(img, start_point, end_point, rect_color, 3)

        
        img = cv2.resize(img,(int(img.shape[1]/2), int(img.shape[0]/2)))
        img_lst.append(img)
    
    print(img_lst[1].shape)
    print(img_lst[0].shape)
    
    img = cv2.hconcat([img_lst[1], img_lst[0]])
    dark_blue = (100,0,0)
    dark_blue1 = (150,0,0)
    cv2.line(img, (int(img.shape[1]/2), 0), (int(img.shape[1]/2), int(img.shape[1])), dark_blue1, thickness=6)
    cv2.line(img, (int(img.shape[1]/4), 0), (int(img.shape[1]/4), int(img.shape[1])), dark_blue, thickness=2)
    cv2.line(img, (int(img.shape[1]*3/4), 0), (int(img.shape[1]*3/4), int(img.shape[1])), dark_blue, thickness=2)
    
    color = (0,200,200)
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'first', (20, 20), font, 0.5, color, 1, cv2.LINE_AA)
    cv2.putText(img, 'last', (int(img.shape[1]/2) +20 , 20), font, 0.5, color, 1, cv2.LINE_AA)
    
    cv2.imshow("first and last imgs",img)
    cv2.waitKey(100)


def capture_imgs(path):
    ## get a timestamp for the file name
    curr_time = datetime.now().strftime("%m_%d__%H_%M_%S")
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

## set up pins to controll blue light
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

L1 = 12#33
L2 = 11#40

GPIO.setup(L1, GPIO.OUT)
GPIO.setup(L2, GPIO.OUT)

###############################################################
#################### main (kind of) ###########################
###############################################################

## init camera
picam2 = Picamera2()

picam2.configure(camera_config="still")
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition":2})
picam2.start()

previous_pic_time = time.perf_counter()
# Start time in YYYY-MM-DD HH:MM:SS
start_date = datetime.now().strftime("%Y-%m-%d")
start_time = datetime.now().strftime("%H:%M")
print(f"Start time: {start_date} {start_time}")

## this goes to the parent folder of where the code is currently running and save the data there
## (so in the git repository)
base_path = f"../{start_date}"
## if we want to specify a path seperatly this would be the way...
# base_path = "/home/pi/Desktop/operant_testing"

## Get the first img - used to choose the ROI
capture_imgs(base_path)
print("finished taking first img...\nwaiting for select ROI(!)")
roi = lrc.get_roi(base_path)

## Allow the user to cancel the ROI selection
if lrc.manual_stop:
    print("\nyou stopped!")
    exit()

## set a time interval for the experiment
time_between_imgs = 240
## To start the loop imidiatly we tweak the previous_pic_time variable
previous_pic_time -= time_between_imgs

## Start the main loop this is the actual experiment
while True:
    ## Save the current the time
    curr_time = time.perf_counter()

    ## If more than X seconds past - take a picture, adjust lighting and update the last capture time
    if curr_time - previous_pic_time > time_between_imgs:
        capture_imgs(base_path)
        print("last img was taken at -", curr_time)
        lrc.loop_through_cams(roi, base_path)
        show(roi, base_path)
        previous_pic_time = curr_time