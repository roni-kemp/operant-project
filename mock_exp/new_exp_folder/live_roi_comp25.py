#%%
import cv2
import os
import numpy as np

#%% MARK: ROI functions

def read_roi_from_file(path):
    """
    Read the ROI from a file.
    Expected format: (x, y, width, height) on the first line.
    """
    with open(path, 'r') as f:
        line = f.read()
        roi_data = line.strip("()[]").split(",")
    return [int(x) for x in roi_data]
    
def select_roi(img_path):
    """
    Open an image and allow the user to select a ROI.
    Returns: (x, y, w, h)
    """
    img = cv2.imread(img_path)
    cv2.namedWindow("SELECT ROI", cv2.WINDOW_NORMAL)
    roi = cv2.selectROI("SELECT ROI", img, showCrosshair=True)
    cv2.destroyAllWindows()
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
    
    ## Save the ROI to a file
    roi_path = os.path.join(base_path, "roi.txt")
    with open(roi_path, 'w') as f:
        f.write(str(roi))
    print(f"ROI saved to {roi_path}")
    
    return roi

def get_roi(base_path):
    """
    Get the ROI from file or ask the user to select one.
    """
    ## if there already is a ROI file - we can use that!
    roi_path = os.path.join(base_path, "roi.txt")

    if os.path.isfile(roi_path):
        user_input = input("\n The file 'roi.txt' already exists...\nDo you want to load that ROI? (Y/n)").strip().lower()
        if user_input in ("", "y"):
            print("using existing file")
            ## continue to load ROI from file
            roi = read_roi_from_file(roi_path)
        else:
            print("Choose new ROI!")
            roi = save_init_roi(base_path)
    else:
        print("No ROI file found. Please select a new ROI.")
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
        cv2.destroyAllWilndows()
    
    return mask


def analyze_roi(roi, base_path, min_color_threshold = 130):
    """
    Analyzes the number of non-black pixels in the specified ROI of the image.
    Applies morphological opening to clean noise.
    """
    img_path = get_last_img_from_folder(base_path)
    img = cv2.imread(img_path)

    thresh_mask = thresholding_grey_img(img, min_color_threshold)
    
    ## Clean up noise
    kernel = np.ones((10,10),np.uint8)
    thresh_mask = cv2.morphologyEx(thresh_mask, cv2.MORPH_OPEN, kernel)

    x, y, w, h = roi
    roi_mask = thresh_mask[y:y+h, x:x+w]

    non_black_pix = len(np.where(roi_mask>0)[0])
    print(f"non black pixels in roi: {non_black_pix}")
    
    return non_black_pix



#%% MARK: testing/main
if __name__ == "__main__":
    # Example usage
    #from matplotlib import pyplot as plt    

    base_path = r"../2025-05-13"
    roi = get_roi(base_path)

    analyze_roi(roi, base_path)

# %%
