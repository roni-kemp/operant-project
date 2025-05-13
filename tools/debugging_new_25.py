import cv2
import numpy as np
import os
from tqdm import tqdm
#%%

## raead settings file 
## gives us roi 
## and...?


# ########## belongs in experimantal #######
# def select_roi(img):
#     """
#     Select a ROI from the image
#     """
#     cv2.namedWindow("SELECT ROI", cv2.WINDOW_NORMAL)
#     ROI = cv2.selectROI("SELECT ROI", img, showCrosshair=True)
#     cv2.destroyWindow("SELECT ROI")
#     return ROI
    
# ROI = select_roi(img)

# def save_roi_to_file(roi, path):
#     """
#     Save the roi to a file
#     """
#     with open(path, 'w') as f:
#         f.write(str(roi))
#     print(f"ROI saved to {path}")
# path = r"C:\Users\aguedad\Desktop\operant imgs\log.txt"
# save_roi_to_file(ROI, path)

###########################################

## readfrom file 
def read_roi_from_file(path):
    """
    Read the roi from a file
    currently expects the format (x,y,width,height) in the first line of the file
    """
    with open(path, 'r') as f:
        roi = f.read()
    roi = roi.strip("()")
    roi = roi.strip("[]")
    roi = roi.split(",")
    roi = [int(x) for x in roi] 
    return roi

## show the roi on the image
def draw_rois(ROI, img, show = False):
    """ 
    Meant to show a full img with the ROI highlighted
    """
    # Draw ROIs
    
    start_point = np.array([ROI[0], ROI[1]])
    end_point = start_point + np.array([ROI[2],ROI[3]])
    # Draw the rois in the image
    rect_color = (212, 220, 127)
    cv2.rectangle(img, start_point, end_point, rect_color, 3)
    
    # for debuging we may want to show a single frame
    if show == True:
        ## clean up old windows, and open new one
        #cv2.destroyAllWindows()
        cv2.namedWindow("first and last imgs", cv2.WINDOW_NORMAL)
        while True:
            cv2.imshow("first and last imgs", img)
            ## if q is pressed break
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        ## close when done
        cv2.destroyAllWindows()
    return img

img_path = r"C:\Users\aguedad\Desktop\operant imgs\new_imgs\03_03__06_23_38.jpg"
img = cv2.imread(img_path)
ROI = read_roi_from_file(r"C:\Users\aguedad\Desktop\operant imgs\log.txt")
draw_rois(ROI, img, show = True)


## show the numer of non black pixels in the roi
def thresholding_grey_img(img, min_threshold, show = False):
    Min = min_threshold
    Max = 255

    lower = np.array(Min)
    upper = np.array(Max)

    # Convert to grey format and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mask = cv2.inRange(gray, Min, Max)
    
    if show:    
        result = cv2.bitwise_and(img, img, mask=mask)
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        cv2.imshow('img', result)
        cv2.waitKey(1)
        cv2.destroyAllWilndows()
    
    return mask


path = r"C:\Users\aguedad\Desktop\operant imgs\log.txt"
ROI = read_roi_from_file(path)

img_path = r"C:\Users\aguedad\Desktop\operant imgs\new_imgs\03_03__06_58_43.jpg"
path = r"C:\Users\aguedad\Desktop\operant imgs\new_imgs"
imgs = os.listdir(path)
imgs_paths = [os.path.join(path, img) for img in imgs]


pxl_count = []

for img_path in imgs_paths:

    img = cv2.imread(img_path)
    copy_img = img.copy()

    draw_rois(ROI, copy_img , show = True)

    min_color_threshold = 130
    thresh_mask = thresholding_grey_img(img, min_color_threshold , show = False)
    roi_mask = thresh_mask[ROI[1]:ROI[1]+ROI[3], ROI[0]:ROI[0]+ROI[2]]

    ## show the roi mask
    cv2.namedWindow("roi_mask", cv2.WINDOW_NORMAL)
    cv2.imshow('roi_mask', roi_mask)
    cv2.waitKey(1)
    # cv2.destroyAllWindows()

    non_black_pix = len(np.where(roi_mask>0)[0])
    print(f"non black pixels in roi: {non_black_pix}")
    pxl_count.append(non_black_pix)

    ## save the roi mask
    img_name = os.path.basename(img_path)
    out_path = os.path.join(path, f"roi_mask_{img_name}")
    cv2.imwrite(out_path, roi_mask)


#%%

time_axis = np.arange(0, len(pxl_count)*4, 4)/60

plt.plot(time_axis, pxl_count)
plt.xlabel("time (h)")
plt.ylabel("Number of plant pixels")
plt.hlines([5000], 0, 14, color='r', linestyle='--')

#pics where taken every 4 minutes, lets create a time axis in hours



## decide what to do base on it 



# %%
