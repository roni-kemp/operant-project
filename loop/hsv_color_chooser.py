import cv2
import numpy as np

def nothing(x):
    pass

# Load image
image = cv2.imread(r"C:\Users\Roni\Downloads\DSC00726.JPG")

cv2.namedWindow("Trackbars")
# Create trackbars for color change
# Hue is from 0-179 for Opencv
cv2.createTrackbar('HMin', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('SMin', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('VMin', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('HMax', 'Trackbars', 0, 179, nothing)
cv2.createTrackbar('SMax', 'Trackbars', 0, 255, nothing)
cv2.createTrackbar('VMax', 'Trackbars', 0, 255, nothing)

# Set default value for Max HSV trackbars
cv2.setTrackbarPos('HMax', 'Trackbars', 179)
cv2.setTrackbarPos('SMax', 'Trackbars', 255)
cv2.setTrackbarPos('VMax', 'Trackbars', 255)

# Initialize HSV min/max values
hMin = sMin = vMin = hMax = sMax = vMax = 0
phMin = psMin = pvMin = phMax = psMax = pvMax = 0



# Create a window
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

while(1):
    # Get current positions of all trackbars
    try:
        hMin = cv2.getTrackbarPos('HMin', 'Trackbars')
        sMin = cv2.getTrackbarPos('SMin', 'Trackbars')
        vMin = cv2.getTrackbarPos('VMin', 'Trackbars')
        hMax = cv2.getTrackbarPos('HMax', 'Trackbars')
        sMax = cv2.getTrackbarPos('SMax', 'Trackbars')
        vMax = cv2.getTrackbarPos('VMax', 'Trackbars')
    except cv.error as e:
        print(f"cv2 error: '''\n{e}'''\nprobably closed window...")
        break
    # Set minimum and maximum HSV values to display
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # Convert to HSV format and color threshold
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)

    # Print if there is a change in HSV value
    if((phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
        print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
        phMin = hMin
        psMin = sMin
        pvMin = vMin
        phMax = hMax
        psMax = sMax
        pvMax = vMax

    # Display result image
    
    cv2.imshow('image', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
print(f"{lower=}")
print(f"{upper=}")
cv2.destroyAllWindows()