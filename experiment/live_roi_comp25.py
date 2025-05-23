#%%
import cv2
import os
import numpy as np
import pickle

#%% MARK: ROI functions

def read_roi_from_file(settings_path):
    """
    Read the ROI from a file.
    Expected format: (x, y, width, height) on the first line.
    """
    ## load the settings
    with open(settings_path, 'rb') as f:
        data_dct = pickle.load(f)
    
    roi_data = data_dct.get("roi", None)
    return roi_data
    
def select_roi(img_path):
    """
    Open an image and allow the user to select a ROI.
    Returns: (x, y, w, h)
    """
    img = cv2.imread(img_path)
    cv2.namedWindow("SELECT ROI", cv2.WINDOW_NORMAL)
    roi = cv2.selectROI("SELECT ROI", img, showCrosshair=True)
    cv2.destroyWindow("SELECT ROI")
    return roi

def get_last_img_from_folder(base_path):
    img_dir = os.path.join(base_path, "imgs")
    image_files = sorted(os.listdir(img_dir))
    if not image_files:
        raise FileNotFoundError("No images found in the imgs directory.")
    image_path = os.path.join(img_dir, image_files[-1])
    return image_path

def save_init_roi(base_path, manual_image_path = None):
    """
    Let the user select a ROI and save it to roi.txt in base_path.
    If no image is specified, use the last image in base_path/imgs.
    """
    global manual_stop
    
    if manual_image_path is None:
        image_path = get_last_img_from_folder(base_path)
    else:
        image_path = manual_image_path
    
    print(f"Loading image for ROI selection: {image_path}")
    roi = select_roi(image_path)

    if roi == (0, 0, 0, 0):
        manual_stop = True

    settings_path = os.path.join(base_path, "settings.pkl")
    if os.path.isfile(settings_path):
        with open(settings_path, 'rb') as f:
            data_dct = pickle.load(f)
        data_dct["roi"] = roi
    else:
        data_dct = {"roi": roi, "grey_threshold": 130}
    with open(settings_path, 'wb') as f:
        pickle.dump(data_dct, f)
    print(f"ROI saved to {settings_path}")
    
    return roi

def get_roi(base_path):
    """
    Get the ROI from file or ask the user to select one.
    """
    ## if there already is a ROI file - we can use that!
    settings_path = os.path.join(base_path, "settings.pkl")

    if os.path.isfile(settings_path):
        roi = read_roi_from_file(settings_path)
        if roi is not None:
            user_input = input("\n there is a ROI in the settings file...\nDo you want to load that ROI? (Y/n)").strip().lower()
            if user_input in ("", "y"):
                print(f"using existing ROI from settings file:\n{settings_path}")
                return roi            
        
        print("No ROI in the seetings file. Choose new ROI!")
        roi = save_init_roi(base_path)
    else:
        print("didn't find the settings file, the default grey_threshold is 130 \nChoose new ROI!")
        roi = save_init_roi(base_path)
    
    return roi
    

## global variable to stop the program
manual_stop = False
#%% MARK: other functions

## show the numer of non black pixels in the roi
def thresholding_grey_img(img, min_threshold, show = False):
    """
    Converts image to grayscale and applies a binary threshold.
    Optionally displays the thresholded result.
    """
    # Convert to grey format and threshold
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    mask = cv2.inRange(gray, min_threshold, 255)
    
    if show:    
        result = cv2.bitwise_and(img, img, mask=mask)
        cv2.namedWindow("img", cv2.WINDOW_NORMAL)
        cv2.imshow('img', result)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    return mask


def analyze_roi(roi, base_path, grey_threshold, show = False):
    """
    Analyzes the number of non-black pixels in the specified ROI of the image.
    Applies morphological opening to clean noise.
    """
    img_path = get_last_img_from_folder(base_path)
    img = cv2.imread(img_path)

    thresh_mask = thresholding_grey_img(img, grey_threshold, show)
    
    ## Clean up noise
    kernel = np.ones((10,10),np.uint8)
    thresh_mask = cv2.morphologyEx(thresh_mask, cv2.MORPH_OPEN, kernel)

    x, y, w, h = roi
    roi_mask = thresh_mask[y:y+h, x:x+w]
    
    non_black_pix = len(np.where(roi_mask>0)[0])
    
    relative_area = non_black_pix / (w * h)
    print(f"relative area of non black pixels in roi: {relative_area:.2%}")
    
    if show:
        cv2.imshow("ROI", roi_mask)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return non_black_pix, round(relative_area*100,2)

def get_grey_threshold(base_path):
    """
    Get the grey threshold from the settings file.
    """
    settings_path = os.path.join(base_path, "settings.pkl")
    if not os.path.isfile(settings_path):
        raise FileNotFoundError(f"Settings file not found: {settings_path}")
    ## load the settings
    with open(settings_path, 'rb') as f:
        data_dct = pickle.load(f)
    grey_threshold = data_dct["grey_threshold"]
    return grey_threshold

#%% MARK: testing/main
if __name__ == "__main__":
    # Example usage
    base_path = r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\mock_exp\2025-05-13"
    roi = get_roi(base_path)
    print(roi)
    grey_thesh = get_grey_threshold(base_path)
    non_black_pix, relative_area = analyze_roi(roi, base_path, grey_thesh)
    print(f"Number of non-black pixels: {non_black_pix}")
    print(f"Relative area of non-black pixels: {relative_area}")

# %%

