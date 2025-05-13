# operant-project
 
## ----- experiment: ------
-- live_roi_comparison
-- log_info
-- single_cam

## ----- tools: -----------
-- live_view
-- hsv_color_chooser
-- grey_thres_chooser

## ----- remove? ----------
-- capture_cam_loop
-- adapter board
-- live_roi_comp_old



----------------
A new experiment should **create** the following folder structure:

```
exp_folder/
├── 250513/
│   ├── roi.txt
│   ├── log.txt
│   ├── imgs/
│   │   ├── 03_02__17_09_52.jpg
│   │   ├── 03_02__17_13_52.jpg
│   │   └── ...
```
----------------

##### TODO:

- [ ] add if statment to the threshold so that we change it depending on the lights on or off
- [ ] resize for choosing ROI and showing, but not for threshold and saveing the image
- [ ] fix bug where creating a new roi doesn't update the first imagen so we don't need to delete every time.
- [ ] check our logging 
	- [ ] threshold, and any other changeing values should be saved to the log file as well.
    - [ ] for each picture add state (time, light on/off, current threshold value, )
- [ ] add the changes to picam to the repo
- [ ] create a debugging fodler 
    - [ ] see the ROI in the original
	- [ ] show the filtered version of the comparison ROI
    - [ ] like in the "live comparison" but for the saved images 
    - [ ] create a video file with all the debugging info (img, the three tiles all in one frame)


-Agueda
- [ ] build new cappa box
- [ ] 
