# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:21:46 2022

@author: Roni
"""

import cv2
import numpy as np

def nothing(x):
    pass

# Load image
image = img
image =  cv.imread(r"C:\Users\Roni\Desktop\1__Croped_1\1_0016_CROPED.jpg")
# Create a window
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

# add hsv filter 
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
lower = np.array([ 89, 100,   0])
upper = np.array([118, 201, 255])
mask = cv2.inRange(hsv, lower, upper)
image = cv2.bitwise_and(image, image, mask=mask)

# cv2.imshow('image', image)
#%


# Create trackbars for color change
cv2.createTrackbar('Min', 'image', 0, 255, nothing)
cv2.createTrackbar('Max', 'image', 0, 255, nothing)

# Set default value for Max trackbars
cv2.setTrackbarPos('Max', 'image', 255)

# Initialize HSV min/max values
Min  = 0
pMin = 0

Max  = 255
pMax = 255


while(1):
    try:
        # Get current positions of all trackbars
        Min = cv2.getTrackbarPos('Min', 'image')
        Max = cv2.getTrackbarPos('Max', 'image')
    except cv.error as e:
        print(f"cv2 error: '''\n{e}'''\nprobably closed window...")
        break
    # Set minimum and maximum HSV values to display
    lower = np.array(Min)
    upper = np.array(Max)

    # Convert to grey format and threshold
    gray = cv.cvtColor(image,cv.COLOR_BGR2GRAY)
    mask = cv2.inRange(gray, Min, Max)
    # result_grey = cv2.bitwise_and(gray, gray, mask=mask)
    result = cv2.bitwise_and(image, image, mask=mask)

    # Print if there is a change in HSV value
    # if ((pMin != Min) | (pMax != Max)):
    #     print(f"changed: {Min=}, {Max=}")
    #     pMin = Min
    #     pMax = Max
    
    cv2.imshow('image', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

print(f"changed: {Min=}, {Max=}")
cv2.destroyAllWindows()

 
