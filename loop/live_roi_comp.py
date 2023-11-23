import cv2
import time
import os
import RPi.GPIO as GPIO
import numpy as np

manual_stop = False

def cropping(frame):
    ## ROI should ideally only be of black background

    ## Open window to select ROI 
    cv2.namedWindow("SELECT ROI", cv2.WINDOW_NORMAL)
    ROI = cv2.selectROI("SELECT ROI", frame, showCrosshair=True)
    ## Parsing ROI to get croped img and close windows 
    x, y, w, h = ROI[0], ROI[1], ROI[2], ROI[3]
    croped_img = frame[y:y+h, x:x+w]
    cv2.destroyWindow("SELECT ROI")
    
    return croped_img, ROI


def save_init_ROIs(path, camera_name, manual_path = None):
    global manual_stop
    
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
        if ROI == (0, 0, 0, 0):
            manual_stop = True
            break
        out_path = path + f"/ROI_{camera_name}_{i+1}.jpg"
        cv2.imwrite(out_path, croped_img)
        cv2.destroyAllWindows()
        ROIs_lst.append(ROI)
    
    log_roi(path + "/ROI_log.txt", data=ROIs_lst)
    
    return ROIs_lst


def load_ROI_dct(path):
    ## there is a better way to do this - but not now:
    roi_lst = []
    with open(path + "/ROI_log.txt", "r") as roi_file:
        for line in roi_file:
            tup = tuple(map(int,line.strip().split(":")[1].strip("(").strip(")").split(', ')))
            roi_lst.append(tup)
    key = line.split(":")[0][0]
    roi_dct = {key:roi_lst[-2:]}
    return roi_dct


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

def compare_2(croped_img, bckgound_img, half):
    """compare 2 imgs and return the number of very different pixls"""
    
    ## only look at the green color space - should help when turning on/off blue light    
    filtered_bckgound_img = hsv_plant_filter(bckgound_img)
    filtered_croped_img = hsv_plant_filter(croped_img)
    
    ## convert both to grayscale
    gray_bkgr = cv2.cvtColor(filtered_bckgound_img, cv2.COLOR_BGR2GRAY)
    gray_curr = cv2.cvtColor(filtered_croped_img, cv2.COLOR_BGR2GRAY)
    
    ## add blurring
    gray_bkgr_blur = cv2.blur(gray_bkgr,(5,5))
    gray_curr_blur = cv2.blur(gray_curr,(5,5))
    
    ## find absolute value diffrence and threshold it
    diff = cv2.absdiff(gray_curr_blur, gray_bkgr_blur)
    
    ret, thresh = cv2.threshold(diff,27,255,cv2.THRESH_BINARY)
    ## Return the num of diff pixels
    pix_num = len(np.where(thresh>0)[0])
   
#     cv2.namedWindow("first_img", cv2.WINDOW_NORMAL)
#     cv2.imshow("first_img", bckgound_img)
#     cv2.namedWindow("last_img", cv2.WINDOW_NORMAL)
#     cv2.imshow("last_img", croped_img)
#     cv2.namedWindow("thresh", cv2.WINDOW_NORMAL)
#     cv2.imshow("thresh", thresh)
    
    thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    font = cv2.FONT_HERSHEY_SIMPLEX
    color = (0,200,200)
    cv2.putText(bckgound_img, 'first', (5, 15), font, 0.5, color, 1, cv2.LINE_AA)
    cv2.putText(croped_img, 'last', (5, 15), font, 0.5, color, 1, cv2.LINE_AA)
    cv2.putText(thresh, 'thresh', (5, 15), font, 0.5, color, 1, cv2.LINE_AA)
    cv2.putText(thresh, f'{pix_num}', (5, 35), font, 0.5, color, 1, cv2.LINE_AA)

    img = cv2.hconcat([bckgound_img, croped_img, thresh])

    cv2.namedWindow(f"{half=}", cv2.WINDOW_NORMAL)
    color = (100,0,0)
    cv2.line(img, (int(croped_img.shape[1]), 0), (int(croped_img.shape[1]), int(img.shape[1])), color, thickness=2)
    cv2.line(img, (int(croped_img.shape[1]*2), 0), (int(croped_img.shape[1]*2), int(img.shape[1])), color, thickness=2)
    cv2.line(img, (int(croped_img.shape[1]*3), 0), (int(croped_img.shape[1]*3), int(img.shape[1])), color, thickness=2)
    
    cv2.imshow(f"{half=}", img)
    cv2.waitKey(100)
    
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
        
        diff_pix_num = compare_2(croped_img, bckgound_img, i)
        print("diff= " + str(diff_pix_num))
        if diff_pix_num>100:
            GPIO.output(light_dct[f"{camera_name}_{i+1}"], 0) ## turn off trhe light
            print(f"light off{camera_name}_{i+1}")

        else:
            GPIO.output(light_dct[f"{camera_name}_{i+1}"], 1)
            print(f"light stays on {camera_name}_{i+1}")
            ## overwrite the old background_img with the updated one
            ## (we do this to take care of noise)
#             cv2.imwrite(bckgrnd_path, croped_img)
            ## since the plant will also move slowly it might not make sense to compare to prev img - we need to comp to first img
            ## lets hope the nois does not get too bad 

def get_ROIs_for_all_cams(path, cam_lst = ["A","B","C","D"]):
    global manual_stop
    
    ## if there already is a ROI file - maybe we can use that!
    if os.path.isfile(path + "/ROI_log.txt"):
        user_input = input("\n The file 'ROI_log.txt' already exists...\ndo you want to load that ROI? (Y/n)")
        if user_input == "y" or user_input == "":
            print("using existing file")
            
            ## continue to load ROI from file
            ROI_dct = load_ROI_dct(path)
            return ROI_dct
        else:
            "Choose new ROI !"
    ROI_dct = {}
    for camera_name in cam_lst:
    
        ROIs = save_init_ROIs(path, camera_name)
        ROI_dct[camera_name] = ROIs
    
    return ROI_dct
            

def loop_through_cams(ROI_dct, light_dct, path):
    for camera_name in list(ROI_dct.keys()):
        ROIs = ROI_dct[camera_name]
        compare_to_prev(path, camera_name, ROIs, light_dct)
    #cv2.destroyAllWindows()

def log_roi(path, data):
    ## also needs fixing...
    """
    function should log all the ROIs so we can troubleshoot later
    and recover if needed
    """  
    camera_name_lst=['B1','B2','C1','C2','D1','D2']
    with open(path, "a") as logger:
        for i in range(len(data)):          
            logger.write(f'{camera_name_lst[i]}:{data[i]}\n')    
