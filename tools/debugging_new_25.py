import cv2
import numpy as np
import os
import pickle
#%%

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
        cv2.namedWindow("first and last imgs", cv2.WINDOW_NORMAL)
        while True:
            cv2.imshow("first and last imgs", img)
            ## if q is pressed break
            key = cv2.waitKey(1)
            if key in (ord('q'), 27):  # 'q' or 'Esc' key
                break
        ## close when done
        cv2.destroyAllWindows()
    return img

## show the numer of non black pixels in the roi
def thresholding_grey_img(img, min_threshold, show = False):
    Min = min_threshold
    Max = 255

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

def get_settings_data(base_path):
    """
    Get the grey threshold from the settings file.
    """
    settings_path = os.path.join(base_path, "settings.pkl")
    if not os.path.isfile(settings_path):
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    ## load the settings
    with open(settings_path, 'rb') as f:
        data_dct = pickle.load(f)
    roi = data_dct["roi"]
    grey_threshold = data_dct["grey_threshold"]

    return roi, grey_threshold

base_path = r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\mock_exp\2025-05-13"
roi, grey_threshold = get_settings_data(base_path)

path = r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\mock_exp\2025-05-13\imgs"
imgs = os.listdir(path)
imgs_paths = [os.path.join(path, img) for img in imgs]

pxl_count = []

for img_path in imgs_paths:

    img = cv2.imread(img_path)
    copy_img = img.copy()

    draw_rois(roi, copy_img , show = False)

    min_color_threshold = 130
    thresh_mask = thresholding_grey_img(img, min_color_threshold , show = False)
    x,y,w,h = roi
    roi_mask = thresh_mask[y:y+h, x:x+w]

    ## show the roi mask
    cv2.namedWindow("roi_mask", cv2.WINDOW_NORMAL)
    cv2.imshow('roi_mask', roi_mask)
    k = cv2.waitKey(1)
    if k in (ord('q'), 27):  # 'q' or 'Esc' key
        break
    
    non_black_pix = len(np.where(roi_mask>0)[0])
    print(f"non black pixels in roi: {non_black_pix}")
    pxl_count.append(non_black_pix)

    ## save the roi mask
    img_name = os.path.basename(img_path)
    out_path = os.path.join(path, f"roi_mask_{img_name}")
    # cv2.imwrite(out_path, roi_mask)

cv2.destroyAllWindows()

#%%
from matplotlib import pyplot as plt

time_axis = np.arange(0, len(pxl_count)*4, 4)/60

plt.plot(time_axis, pxl_count)
plt.xlabel("time (h)")
plt.ylabel("Number of plant pixels")


# pics where taken every 4 minutes, lets create a time axis in hours

