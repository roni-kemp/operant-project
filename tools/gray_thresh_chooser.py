# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:21:46 2022

@author: Roni
"""
#%%
import cv2
import numpy as np

def nothing(x):
    pass

# Load image
image =  cv2.imread(r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\operant_imgs\A\07_17__18_07_57.jpg")
# Create a window
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

# Add hsv filter 
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
lower = np.array([ 89, 100,   0])
upper = np.array([118, 201, 255])
mask = cv2.inRange(hsv, lower, upper)
# image = cv2.bitwise_and(image, image, mask=mask)


while True:
    cv2.imshow('image', image)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cv2.destroyAllWindows()

#%%

# Create a window
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

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
    except cv2.error as e:
        print(f"cv2 error: '''\n{e}'''\nprobably closed window...")
        break
    # Set minimum and maximum HSV values to display
    lower = np.array(Min)
    upper = np.array(Max)

    # Convert to grey format and threshold
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask = cv2.inRange(gray, Min, Max)
    # result_grey = cv2.bitwise_and(gray, gray, mask=mask)
    result = cv2.bitwise_and(image, image, mask=mask)
    
    cv2.imshow('image', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

print(f"changed: {Min=}, {Max=}")
cv2.destroyAllWindows()

 
