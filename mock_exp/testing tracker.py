#%%
import cv2
import os
import glob
from datetime import datetime
# === CONFIGURATION ===
image_folder = r"C:\Users\Roni\Desktop\transfer\E1\imgs"  # Change this to your folder path
image_extension = "*.jpg"  # or *.png, *.jpeg, etc.
tracker_type = 'CSRT'  # Choose from: MIL, KCF, CSRT


# === SETUP TRACKER ===
tracker_types = {
    'MIL': cv2.TrackerMIL_create,
    'KCF': cv2.TrackerKCF_create,
    'CSRT': cv2.TrackerCSRT_create
}
tracker = tracker_types[tracker_type]()

# === LOAD IMAGE FILES ===
image_files = sorted(glob.glob(os.path.join(image_folder, image_extension)))
if not image_files:
    print("Error: No images found in folder.")
    exit()

# === INITIALIZATION ===
first_frame = cv2.imread(image_files[0])
if first_frame is None:
    print("Error: Could not load the first image.")
    exit()

bbox = cv2.selectROI("Tracking", first_frame, False)
tracker.init(first_frame, bbox)

track = []
frames = []

# === MAIN LOOP ===
for img_path in image_files:
    frame = cv2.imread(img_path)
    if frame is None:
        continue

    time_stamp = os.path.splitext(os.path.basename(img_path))[0]
    # "05_19__15_35_42.jpg"
    time_stamp = datetime.strptime(time_stamp, "%m_%d__%H_%M_%S")
    str_time = time_stamp.strftime("%d/%m    %H:%M:%S")

    success, bbox = tracker.update(frame)
    if success:
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 200, 255), 2, 1)
        cv2.putText(frame, str_time, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 1)
    else:
        cv2.putText(frame, "Lost", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    center = (x + w // 2, y + h // 2)
    track.append(center)
    for i in range(len(track)-60, len(track),6):

        if i >= 0:
            ## stronger color the closer to the end
            color = (250, 50, 255 - (i - len(track) + 20) * 10)
            # color = (0,0,255)
            cv2.circle(frame, track[i], 2, color, -1)
        
    frames.append(frame)
    cv2.imshow("Tracking", frame)
    key = cv2.waitKey(30) & 0xFF
    if key == 27:  # ESC
        break
cv2.destroyAllWindows()

with open('track1.txt', 'w') as f:
    for item in track:
        f.write(f"{item[0]},{item[1]}\n")

#%% MARK: save video mp4

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output1.mp4', fourcc, 30.0, (first_frame.shape[1], first_frame.shape[0]))
for frame in frames:
    out.write(frame)
out.release()
