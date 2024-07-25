## should recive the path to image folder
## and roi log file
## if we log anything else - that too 

## should create a video of the entire frame with the roi compraison (first, last,diff) at the bottom
#%%

import cv2
import numpy as np
import os
from tqdm import tqdm

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
    ## TODO: 
        # change this into a settings file - json/pickle/dictionary 
        # so we can add and remove settings withouth breaking the format

def draw_rois(ROIs_dct, img, show = False):
    """ 
    Meant to show a full img of the last capture with the ROIs highlighted
    """
    
    ROIs = ROIs_dct["B"]

    # Draw ROIs
    for i in range(2):
        ROI = ROIs[i]
        start_point = np.array((ROI[0]+i*int(img.shape[1]/2),ROI[1])) 
        end_point = start_point + np.array((ROI[2],ROI[3]))
        # Draw the rois in the image
        rect_color = (212, 220-(100*i), 127+(100*i))
        cv2.rectangle(img, start_point, end_point, rect_color, 3)
    
    # for debuging we may want to show a single frame
    if show == True:
        ## clean up old windows, and open new one
        #cv2.destroyAllWindows()
        cv2.namedWindow("first and last imgs", cv2.WINDOW_NORMAL)
        while True:
            cv2.imshow("first and last imgs", img)
            ## if q is pressed break
            key = cv2.waitKey(0)
            if key == ord('q'):
                break
        ## close when done
        cv2.destroyAllWindows()
    return img

def loop_over_exp_folder(ROIs_dct, path, show = False, save = True):
    img_folder_path = path + "/B" 
    files_lst = os.listdir(img_folder_path)
    sorted_lst = sorted(files_lst)
    num_files = len(sorted_lst)
    
    img_paths = [os.path.join(img_folder_path, sorted_lst[i]) for i in range(num_files)]
    imgs_lst = []
    for i in tqdm(range(1000)):#num_files)):
        img = cv2.imread(img_paths[i])

        ## Draw the rois on the image
        img = draw_rois(ROIs_dct, img, show = False)

        ## Show the comparison image


        imgs_lst.append(img)



        if show == True:
            cv2.imshow("img", img)
            ## if q is pressed break
            key = cv2.waitKey(10)
            if key == ord('q'):
                break
    
    if show == True:
        ## close when done
        cv2.destroyAllWindows()
    if save == True:
        out_path = path + "/full_imgs_with_ROIs.mp4"
        out = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*'mp4v'), 10.0, (img.shape[1], img.shape[0]))
        for i in range(len(imgs_lst)):
            out.write(imgs_lst[i])
        out.release()


## TODO:
    # add the comparison to the first frame


path = r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\operant_imgs\New"
 
ROIs_dct = load_ROI_dct(path)

loop_over_exp_folder(ROIs_dct, path)#, show = True, save = False)
