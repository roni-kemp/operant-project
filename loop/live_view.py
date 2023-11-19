import cv2
import os
import numpy as np

path = "/home/pi/Desktop/agueda_imgs/__new_imgs__"
roi_lst = []
with open(path + "/ROI_log.txt", "r") as roi_file:
    for line in roi_file:
        tup = tuple(map(int,line.strip().split(":")[1].strip("(").strip(")").split(', ')))
        roi_lst.append(tup)

print(roi_lst[-2:])

def hsv_plant_filter(img):
    f_img = img.copy()
    hsv = cv2.cvtColor(f_img, cv2.COLOR_BGR2HSV) 
    
    # Set lower and upper color limits
    lower_val = np.array([0,0,110])
    upper_val = np.array([179,200,190])
    
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_val, upper_val)
    
    # Apply mask to original image - this shows the chosen color with black blackground
    filtered_hsv = cv2.bitwise_and(f_img, f_img, mask= mask)
    return filtered_hsv

# define a video capture object
vid = cv2.VideoCapture(0)

first_img_path = path + "/B/"+ os.listdir(path + "/B")[0]
first_img = cv2.imread(first_img_path)

## only look at the green color space - should help when turning on/off blue light    
filtered_bckgound_img = hsv_plant_filter(first_img)

## convert both to grayscale
gray_bkgr = cv2.cvtColor(filtered_bckgound_img, cv2.COLOR_BGR2GRAY)

## add blurring
gray_bkgr_blur = cv2.blur(gray_bkgr,(5,5))


while True:
    
    # Capture the video frame
    # by frame
    ret, frame = vid.read()
    
    ## only look at the green color space - should help when turning on/off blue light    
    filtered_frame = hsv_plant_filter(frame)

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