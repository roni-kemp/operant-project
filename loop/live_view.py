"""
this is meant as a debugging tool
to see a live view of the camera feed and the different filtered versions

TO DO:
add ROI marking to the img
can use - lrc.load_ROI(path)
"""

import cv2
import os
import numpy as np

import live_roi_comp as lrc

path = "/home/pi/Desktop/operant_testing"

# define a video capture object
vid = cv2.VideoCapture(0)

first_img_path = path + "/B/"+ os.listdir(path + "/B")[0]
first_img = cv2.imread(first_img_path)

## only look at the green color space - should help when turning on/off blue light    
filtered_bckgound_img = lrc.hsv_plant_filter(first_img)

## convert both to grayscale
gray_bkgr = cv2.cvtColor(filtered_bckgound_img, cv2.COLOR_BGR2GRAY)

## add blurring
gray_bkgr_blur = cv2.blur(gray_bkgr,(5,5))


while True:
    
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    
    ## only look at the green color space - should help when turning on/off blue light    
    filtered_frame = lrc.hsv_plant_filter(frame)

    ## convert both to grayscale
    gray_frame = cv2.cvtColor(filtered_frame, cv2.COLOR_BGR2GRAY)
    gray_frame_blur = cv2.blur(gray_frame,(5,5))
    
    ## find absolute value diffrence and threshold it
    diff = cv2.absdiff(gray_frame_blur, gray_bkgr_blur)

    ret, thresh = cv2.threshold(diff,27,255,cv2.THRESH_BINARY)

    cv2.namedWindow("first_img", cv2.WINDOW_NORMAL)
    cv2.imshow("first_img", gray_bkgr_blur)

    cv2.namedWindow("last_img", cv2.WINDOW_NORMAL)
    cv2.imshow("last_img", gray_frame_blur)

    cv2.namedWindow("thresh", cv2.WINDOW_NORMAL)
    cv2.imshow("thresh", thresh)

    # Display the resulting frame
    cv2.imshow('frame', frame)
      
    #press q to stop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()