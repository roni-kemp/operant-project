import cv2
import time
import os
# import RPi.GPIO as GPIO
import numpy as np

def cropping(frame):
    ## ROI should ideally only be of black background

    ## select roi and close window
    cv2.namedWindow("SELECT ROI", cv2.WINDOW_NORMAL)
    ROI = cv2.selectROI("SELECT ROI", frame, showCrosshair=True)

    x, y, w, h = ROI[0], ROI[1], ROI[2], ROI[3]
    croped_img = frame[y:y+h, x:x+w]
    cv2.destroyWindow("SELECT ROI")
    return croped_img, ROI


def save_init_ROIs(path, camera_name, manual_path = None):
    if manual_path == None:
        curent_path = path + "/" + camera_name
        img_list = os.listdir(curent_path)
        img_list.sort()
        full_path = curent_path + "/" + img_list[-1]
        print(full_path)
    else:
        full_path = manual_path
    img = cv2.imread(full_path)

    half_width = int(img.shape[1]/2)

    img_1 = img[:: , :half_width]
    img_2 = img[:: , half_width:]
    img_halfes = [img_1, img_2]

    ROIs_lst = []
    for i in range(2):
        croped_img, ROI = cropping(img_halfes[i])
        out_path = path + f"/ROI_{camera_name}_{i+1}.jpg"
        cv2.imwrite(out_path, croped_img)
        cv2.destroyAllWindows()
        ROIs_lst.append(ROI)
    
    return ROIs_lst

def hsv_plant_filter(img):
    f_img = img.copy()
    hsv = cv2.cvtColor(f_img, cv2.COLOR_BGR2HSV) 
    
    # Set lower and upper color limits
    lower_val = np.array([136,89,98])
    upper_val = np.array([179,151,190])
    
    # Threshold the HSV image to get only green colors
    mask = cv2.inRange(hsv, lower_val, upper_val)
    
    # Apply mask to original image - this shows the chosen color with black blackground
    filtered_hsv = cv2.bitwise_and(f_img, f_img, mask= mask)
    return filtered_hsv

def compare_2(croped_img, bckgound_img):
    """compare 2 imgs and return the number of very different pixls"""
    
    ## only look at the green color space - should help when turning on/off blue light    
    filtered_bckgound_img = hsv_plant_filter(bckgound_img)
    filtered_croped_img = hsv_plant_filter(croped_img)
    
    ## convert both to grayscale
    gray_bkgr = cv2.cvtColor(filtered_bckgound_img, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(filtered_croped_img, cv2.COLOR_BGR2GRAY)

    ## find absolute value diffrence and threshold it
    diff = cv2.absdiff(gray_curr, gray_bkgr)
    ret, thresh = cv2.threshold(diff,27,255,cv2.THRESH_BINARY)

    ## Return the num of diff pixels
    pix_num = len(np.where(thresh>0)[0])
    return pix_num


def compare_to_prev(path, camera_name, ROIs, light_dct):
    curent_path = path + "/" + camera_name
    img_list = os.listdir(curent_path)
    img_list.sort()
    full_path = curent_path + "/" + img_list[-1]
    img = cv2.imread(full_path)
    half_width = int(img.shape[1]/2)

    img_1 = img[:: , :half_width]
    img_2 = img[:: , half_width:]
    img_halfes = [img_1, img_2]

    for i in range(2):
        curr_img = img_halfes[i]
        ROI = ROIs[i]
        x, y, w, h = ROI[0], ROI[1], ROI[2], ROI[3]
        croped_img = curr_img[y:y+h,x:x+w]
        bckgrnd_path = path + f"/ROI_{camera_name}_{i+1}.jpg"
        bckgound_img = cv2.imread(bckgrnd_path)
        
        diff_pix_num = compare_2(croped_img, bckgound_img)
        
        if diff_pix_num>200:
            #GPIO.output(light_dct[f"{camera_name}_{i+1}"], 1) ## turn off trhe light
            print(f"light off{camera_name}_{i+1}")
        else:
            #GPIO.output(light_dct[f"{camera_name}_{i+1}"], 0)
            print("light stays on")
            ## overwrite the old background_img with the updated one
            ## (we do this to take care of noise)
#             cv2.imwrite(bckgrnd_path, croped_img)
            ## since the plant will also move slowly it might not make sense to compare to prev img - we need to comp to first img
            ## lets hope the nois does not get too bad 

def get_ROIs_for_all_cams(cam_lst = ["A","B","C","D"]):
    path = "/home/pi/Desktop/agueda_imgs/__new_imgs__"
    ROI_dct = {}
    for camera_name in cam_lst:
        ROIs = save_init_ROIs(path, camera_name)
        ROI_dct[camera_name] = ROIs
    
    return ROI_dct




def loop_through_cams(ROI_dct):
    
    path = "/home/pi/Desktop/agueda_imgs/__new_imgs__"
    
    ## update this dct when actually using for then one box!
    light_dct = {"A_1":L1, "A_2":L2, "B_1":L3, "B_2":L3, "C_1":L3, "C_2":L3,"D_1":L3,"D_2":L3}
    for camera_name in list(ROI_dct.keys()):
        ROIs = ROI_dct[camera_name]
        compare_to_prev(path, camera_name, ROIs, light_dct)

## new 


def log_roi(path, data):
    """
    function should log all the ROIs so we can troubleshoot later
    and recover if 
    """
    
    camera_name_lst=['A1', 'A2','B1','B2','C1','C2','D1','D2']
    with open(path, "a") as logger:
        for i in range(len(data)):          
            logger.write(f'{camera_name_lst[i]}:{data[i]}\n')    


    [((200,0), (10,10)), ((200,0), (10,10))]

#%% testing on pc (not pi...)

roni_pc_path = r"C:/Users/Roni/Desktop/Roni_new/python scripts/pavlovian sunflowers/operant-project/operant_imgs/A/07_17__18_07_57.jpg"


img = cv2.imread(roni_pc_path)

croped_img, ROI = cropping(img)
#%%

cv2.namedWindow("testing", cv2.WINDOW_NORMAL)
cv2.imshow("testing", croped_img)
cv2.waitKey(1)

#%%



filt_img = hsv_plant_filter(croped_img)
#show image
cv2.namedWindow("testing", cv2.WINDOW_NORMAL)
cv2.imshow("testing", filt_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

#%%



#GPIO.setmode(GPIO.BOARD)
#GPIO.setwarnings(False)

L1 = 33
L2 = 40
L3 = 38 #...

#GPIO.setup(L1, GPIO.OUT)
#GPIO.setup(L2, GPIO.OUT)
#GPIO.setup(L3, GPIO.OUT) #(dont forget to add the rest!)


# ROIs = save_init_ROIs(path, camera_name)
# ROI_dct = get_ROIs_for_all_cams()
# ROI_dct = {'A': [(217, 263, 147, 226), (239, 276, 55, 138)], 'B': [(365, 448, 86, 79), (220, 231, 63, 43)], 'C': [(180, 149, 56, 43), (152, 131, 64, 52)], 'D': [(128, 103, 62, 58), (80, 53, 101, 86)]}
# loop_through_cams(ROI_dct)