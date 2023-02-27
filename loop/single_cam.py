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

def save_imgs(parent_path, f_name, width, height):
    was_ok = True
    ## handle folder path 
    directory_name = "B"
    path = os.path.join(parent_path, directory_name)
    ## Check if the folder exists
    ## Create empty folders if not
    if not os.path.isdir(path):
        os.makedirs(path)
        print("created folder")
    else:
        print("folder exists")
    
    camera = cv2.VideoCapture(0)
    
    try:
        assert camera.isOpened()
        ret, frame = camera.read()
        
        if ret == True:
            file_path = path + "//" + f_name +".jpg"
            cv2.imwrite(file_path, frame)
            print(f"camera was OK")
#             my_logging((f_name, directory_name, "worked"))
#             time.sleep(0.5)
            
        else:
            print(f"failed,{f_name} try again...")                    
#             my_logging((f_name, directory_name, "failed"))
            was_ok = False
            
    
    except AssertionError:
        print(f"{30*'#'}\n assertion error with video capture\n{30*'#'}")
#         logging.info(30*'-')
#         logging.exception('')
        was_ok = False
        
    
    except:
        print("error when retrying...")
#         logging.info(30*'-')
#         logging.exception('')
        was_ok = False
        

#     my_logging(f"{cnt} of {self.camNum} worked at {f_name}, temp was {check_temp()} deg.\n")
    camera.release()
    return was_ok
    
def show(ROI_dct):
    cv2.destroyAllWindows()
    my_path = "/home/pi/Desktop/agueda_imgs/__new_imgs__"

    ROIs = ROIs_dct["B"]
    for i in range(-1,1):
        img_path = os.listdir(my_path + "/B")[i]
        
        img = cv2.imread(my_path + f"/B/{img_path}")
        
        for i in range(2):#ROIs:
            ROI = ROIs[i]
            start_point = np.array((ROI[0]+i*int(img.shape[1]/2),ROI[1])) 
            end_point = start_point + np.array((ROI[2],ROI[3]))

            cv2.rectangle(img, start_point, end_point, (212, 220, 127), 3)

        img = cv2.resize(img,(int(img.shape[1]/2), int(img.shape[0]/2)))
        cv2.imshow(f"{img_path}",img)
        cv2.waitKey(1000)

def capture_imgs():
    ## get a timestamp for the file name
   
    now = datetime.now()

    curr_time = now.strftime("%m_%d__%H_%M_%S")
    print("Current Time =", curr_time)
    
    ## loop and check if there was an error in capturing and saving the img, if so retry
    my_path = "/home/pi/Desktop/agueda_imgs/__new_imgs__"
    while True:
        was_ok = save_imgs(my_path ,curr_time, 1280, 720)
        if was_ok:
            break
        else:
            print("was not ok... retry...")
            time.sleep(2)
    print("was ok! NEXT!")

# # def main():
start = time.perf_counter()
print("starting loop-", time.ctime())
capture_imgs()

print("finished taking first img...\nwaiting for select ROI")

ROIs_dct = lrc.get_ROIs_for_all_cams(["B"])
light_dct = {"B_1":L1, "B_2":L2}
lrc.loop_through_cams(ROIs_dct, light_dct)

while True:

    if time.perf_counter()- start > 30:
        start = time.perf_counter()
        capture_imgs()
        print("last img was taken at -", time.ctime())
        lrc.loop_through_cams(ROIs_dct, light_dct)
        show(ROIs_dct)



    

