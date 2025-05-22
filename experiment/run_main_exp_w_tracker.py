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
        for i in range(10): ## give the camera a few tries to get a stable image
            frame = picam2.capture_array("main")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        ###### resize the image - why though? ######
        # scale_percent = 30 # [%]
        # width = int(frame.shape[1] * scale_percent / 100)
        # height = int(frame.shape[0] * scale_percent / 100)
        # dim = (width, height)
        # frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
        ############################################

        file_path = os.path.join(path, f_name)
        cv2.imwrite(file_path, frame)
                
    except AssertionError:
        print(f"{30*'#'}\n assertion error with video capture\n{30*'#'}")
        ## We should log this
        was_ok = False
        
    except:
        print("error when retrying...")
        was_ok = False
        ## We should log this

    return was_ok, frame

def show_roi(roi, base_path, save = False):
    ## get last img from the folder
    path = os.path.join(base_path, "imgs")
    img_path = sorted(os.listdir(path))[-1]
    img = cv2.imread(os.path.join(path, img_path))

    x, y, w, h = roi
    croped_img = img[y:y+h, x:x+w]

    grey_thesh = lrc.get_grey_threshold(base_path)
    croped_thresholded = lrc.thresholding_grey_img(croped_img, grey_thesh)
    croped_thresholded = cv2.cvtColor(croped_thresholded, cv2.COLOR_GRAY2BGR)

    img = cv2.hconcat([croped_img, croped_thresholded])
    
    dark_blue = (150,0,0)
    cv2.line(img, (int(img.shape[1]/2), 0), (int(img.shape[1]/2), int(img.shape[1])), dark_blue, thickness=6)

    _, relative_white = lrc.analyze_roi(roi, base_path, grey_thesh)
    cv2.putText(img, f"relative white: {relative_white}%", (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,200,200), 1, cv2.LINE_AA)

    ## show the image
    cv2.namedWindow("last img", cv2.WINDOW_NORMAL)
    cv2.imshow("last img", img)
    cv2.waitKey(100)

    if save:
        ## save the image
        path = os.path.join(base_path, "croped_rois")
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, "roi_"+img_path)
        cv2.imwrite(file_path, img)
    return img

def capture_imgs(path):
    ## get a timestamp for the file name
    curr_time = datetime.now().strftime("%m_%d__%H_%M_%S")
    print("Current Time =", curr_time)
    
    img_file_name = f"{curr_time}.jpg"
    ## loop and check if there was an error in capturing and saving the img
    ## if there was an error retry
    while True:
        was_ok, frame = save_imgs(path, img_file_name, 1280, 720)
        if was_ok:
            break
        else:
            print("was not ok... retry...")
            time.sleep(2)
    print("was ok! NEXT!")
    return frame

def init_log(log_path):
    with open(log_path, 'w') as f:
        f.write("time, pixel_cnt, relative_pixel_value, light_status\n")

def log_data(log_path, values):
    with open(log_path, 'a') as f:
                ## time, pixel_cnt, pixel_value, light_status
        f.write(f"{values[0]}, {values[1]}, {values[2]}, {values[3]}\n")


## set up pins to controll light
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
L1 = 4
GPIO.setup(L1, GPIO.OUT)

###############################################################
#################### main (kind of) ###########################
###############################################################

## Init light
GPIO.output(L1, GPIO.LOW)
Light_status = "off"

## Init camera
picam2 = Picamera2()

picam2.configure(camera_config="still")
picam2.set_controls({"AfMode": controls.AfModeEnum.Manual, "LensPosition":2})
picam2.start()

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
first_frame = capture_imgs(base_path)
print("finished taking first img...\nwaiting for select ROI(!)")
roi = lrc.get_roi(base_path)

## Initialize the log file
log_path = os.path.join(base_path, "log.txt")
init_log(log_path)

## Allow the user to cancel the ROI selection
if lrc.manual_stop:
    print("\nyou stopped!")
    exit()

## set a time interval for the experiment and init timer
time_between_imgs = 240
previous_pic_time = time.perf_counter()
## To start the loop imidiatly we tweak the previous_pic_time variable
previous_pic_time -= time_between_imgs


# === SETUP TRACKER ===
## Get tracking ROI from the first frame
track_bbox = cv2.selectROI("Tracking", first_frame, False)
## Create a tracker object
tracker = cv2.TrackerCSRT_create()
tracker.init(first_frame, track_bbox)

## Start the main loop this is the actual experiment
while True:
    ## Save the current the time
    curr_time = time.perf_counter()

    ## If more than X seconds past - take a picture, adjust lighting and update the last capture time
    if curr_time - previous_pic_time > time_between_imgs:
        curr_frame = capture_imgs(base_path)
        ## tracking:
        success, bbox = tracker.update(curr_frame)
        if success:
            (x, y, w, h) = [int(v) for v in bbox]
            center = (x + w // 2, y + h // 2)

        img_time = datetime.now().strftime("%m/%d - %H_%M_%S")
        print(f"last img was taken at:\n{img_time}")

        ## if the x coordinates are not in the ROI - turn on the light
        x_center = center[0]
        # y_center = center[1]
        if x_center < roi[0] or x_center > roi[0] + roi[2]:
            GPIO.output(L1, GPIO.HIGH)
            Light_status = "on"
        else:
            GPIO.output(L1, GPIO.LOW)
            Light_status = "off"

        values = (img_time, center, "relative_white", Light_status)
        log_data(log_path, values)

        previous_pic_time = curr_time