# -*- coding: utf-8 -*-
"""
Created on Tue Aug  9 12:21:46 2022

@author: Roni
"""
#%%
import cv2
import numpy as np
import pickle
import tkinter as tk
from tkinter import filedialog, messagebox

def nothing(x):
    pass

# Load image
image =  cv2.imread(r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\mock_exp\2025-05-13\closed_lid\05_13__17_40_23.jpg")

# Create a window
cv2.namedWindow("image", cv2.WINDOW_NORMAL)

# Create trackbars for color change
cv2.createTrackbar('Min', 'image', 0, 255, nothing)
cv2.createTrackbar('Max', 'image', 0, 255, nothing)

# Set default value for Min/Max trackbars
cv2.setTrackbarPos('Min', 'image', 0)
cv2.setTrackbarPos('Max', 'image', 255)

# Initialize grey Min/Max values
Min  = 0
Max  = 255

while True:
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
    
    ## morphological operation to remove small object noise 
    kernel_size = int(min(gray.shape)*0.008) ## 0.8% of the image size
    kernel_size = max(2, kernel_size)
    kernel = np.ones((kernel_size, kernel_size),np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # result_grey = cv2.bitwise_and(gray, gray, mask=mask)
    result = cv2.bitwise_and(image, image, mask=mask)
    
    cv2.imshow('image', result)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

#%% MARK: UI

# Create and hide the root window
root = tk.Tk()
root.withdraw()

# Create a temporary top-level window to bring dialogs to the front
top = tk.Toplevel()
top.withdraw()                # Hide it
top.lift()                    # Bring it to the front
top.attributes('-topmost', True)  # Always on top
top.after_idle(top.attributes, '-topmost', False)  # Reset after idle

# Show message box with the dummy top-level window as parent
response = messagebox.askquestion(
    "Save Threshold",
    "Do you want to save the threshold?",
    icon='warning',
    parent=top
)

if response == 'yes':
    file_path = filedialog.asksaveasfilename(
        title="Save Threshold Settings",
        defaultextension=".pkl",
        initialfile="settings.pkl",
        filetypes=[("Pickle files", "*.pkl"), ("All files", "*.*")],
        parent=top  # Ensure dialog is also frontmost
    )
    
    if file_path:
        print(f"User chose to save at:\n{file_path}")
        dct = {"grey_threshold": Min}
        with open(file_path, 'wb') as f:
            pickle.dump(dct, f)
    else:
        print("User canceled the save dialog.")
else:
    print("User chose NOT to Save.")

top.destroy()  # Clean up

