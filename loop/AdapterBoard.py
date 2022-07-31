import RPi.GPIO as gp
import os
import cv2 as cv 
import numpy as np
import time
import logging 


class MultiAdapter:
    
    logging.basicConfig(filename='/home/pi/Desktop/agueda_imgs/example1.log', level=logging.DEBUG)
    
    
    camNum = 4
    adapter_info = {   "A":{   "i2c_cmd":"i2cset -y 1 0x70 0x00 0x04",
                                "gpio_sta":[0,0,1],
                        },
                    "B":{
                            "i2c_cmd":"i2cset -y 1 0x70 0x00 0x05",
                            "gpio_sta":[1,0,1],
                        },
                    "C":{
                            "i2c_cmd":"i2cset -y 1 0x70 0x00 0x06",
                            "gpio_sta":[0,1,0],
                        },
                    "D":{
                            "i2c_cmd":"i2cset -y 1 0x70 0x00 0x07",
                            "gpio_sta":[1,1,0],
                        },
                 }
   
    width = 320
    height = 240
    
    def release_all(self):
        for i in range(self.camNum):
            self.choose_channel(chr(65+i)) 
            self.camera.release()
   
    def __init__(self):
       #gp.setwarnings(False)
        gp.setmode(gp.BOARD)
        gp.setup(7, gp.OUT)
        gp.setup(11,gp.OUT)
        gp.setup(12,gp.OUT)
       

    def choose_channel(self,index):
        channel_info = self.adapter_info.get(index)
        if channel_info == None:
            print("Can't get this info")
        os.system(channel_info["i2c_cmd"]) # i2c write
        gpio_sta = channel_info["gpio_sta"] # gpio write
        gp.output(7, gpio_sta[0])
        gp.output(11, gpio_sta[1])
        gp.output(12, gpio_sta[2])

    def init(self,width,height):
        for i in range(self.camNum):
            self.height = height
            self.width = width
            self.choose_channel(chr(65+i)) 
            self.camera.set(3, self.width)
            self.camera.set(4, self.height)
            ret, frame = self.camera.read()
            if ret == True:
                print("camera %s init OK" %(chr(65+i)))
                pname = "image_"+ chr(65+i)+".jpg"
                cv.imwrite(pname,frame)
    
    def new_preview(self):
        start = time.perf_counter()
        for i in range(4):
            cv.namedWindow(chr(65+i), cv.WINDOW_NORMAL)
        ## update a window with output of each camera for 20 frames 
        for i in range(4):
            self.choose_channel(chr(65+i)) 
            for j_ in range(200):
                
                ret, frame = self.camera.read()
                cv.imshow(chr(65+i), frame)
                
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        del frame
        self.camera.release()
        cv.destroyAllWindows()
        print(time.perf_counter()-start)
    
    def preview(self):
        camera = cv.VideoCapture(0)
        font                   = cv.FONT_HERSHEY_PLAIN
        fontScale              = 1
        fontColor              = (255,255,255)
        lineType               = 1
        factor  = 20
        black = np.zeros(((self.height+factor)*2, self.width*2, 3), dtype= np.uint8) 
        i = 0
        
        camera.set(3, self.width)
        camera.set(4, self.height)
                
        while True:
            self.choose_channel(chr(65+i)) 
            ret, frame = camera.read()
            ret, frame = camera.read()
            ret, frame = camera.read()
            print(ret)
            frame.dtype=np.uint8
            if i == 0:
                black[factor:factor+self.height, 0:self.width, :] = frame
                bottomLeftCornerOfText = (factor,factor)
                index = chr(65+i)
            elif i == 1:
                black[factor:factor+self.height, self.width:self.width*2,:] = frame
                bottomLeftCornerOfText = (factor + self.width, factor)
                index = chr(65+i)
            elif i == 2:
                black[factor*2+self.height:factor*2+self.height*2, 0:self.width,:] = frame
                bottomLeftCornerOfText = (factor, factor*2+self.height)
                index = chr(65+i)
            elif i == 3:
                black[factor*2+self.height:factor*2+self.height*2, self.width:self.width*2,:] = frame
                bottomLeftCornerOfText = (factor+self.width, factor*2+self.height)
                index = chr(65+i)
            i = i+1
            if i==self.camNum:
                i = 0
            cv.putText(black,'CAM '+index, bottomLeftCornerOfText, font, fontScale,fontColor,lineType)
            cv.imshow("Arducam Multi Camera Demo",black)
            if cv.waitKey(1) & 0xFF == ord('q'):
                del frame
                camera.release()
                cv.destroyAllWindows()
                break

    def save_imgs(self, parent_path, f_name, width,height):
        camera = cv.VideoCapture(0)
        # Check if the folder exists
        # Create empty folders if not
        for i in range(self.camNum):
            directory_name = chr(65+i)
            path = os.path.join(parent_path, directory_name)
            
            if not os.path.isdir(path):
                os.makedirs(path)
                print("created folder " + chr(65+i))
            else:
                print("folder exists - " + chr(65+i))
        # logging data
        cnt = 0
        
#         print(self.camera.get(cv.CAP_PROP_AUTO_EXPOSURE))
#         self.camera.set(cv.CAP_PROP_AUTO_EXPOSURE, 1.0)
#         self.camera.set(cv.CAP_PROP_EXPOSURE, 50000.0)
#         print(self.camera.get(cv.CAP_PROP_EXPOSURE))
#         print(self.camera.get(cv.CAP_PROP_AUTO_EXPOSURE))
        #CAP_PROP_AUTO_EXPOSURE 
        # Take imgs    
        for i in range(self.camNum):
            try:
                self.height = height
                self.width = width
                self.choose_channel(chr(65+i))
                time.sleep(0.5)
                camera.set(3, self.width)
                camera.set(4, self.height)
                ## manual brightness controll -needs clock                
#                 if i == 0:
#                     camera.set(cv.CAP_PROP_BRIGHTNESS, 20)
#                 if i == 1:
#                     camera.set(cv.CAP_PROP_BRIGHTNESS, 20)
#                 if i == 2:
#                     camera.set(cv.CAP_PROP_BRIGHTNESS, 50)
#                 if i == 3:
#                     camera.set(cv.CAP_PROP_BRIGHTNESS, 50)
                ret, frame = camera.read()
                if ret == True:
                    directory_name = chr(65+i)
                    path = os.path.join(parent_path, directory_name)
                   
                    pname = path + "//" + f_name +".jpg"
                    cv.imwrite(pname,frame)
                    print(f"camera {chr(65+i)} OK")
                    my_logging((f_name, directory_name, "worked"))
                    time.sleep(0.5)
                    cnt += 1
                else:
                    print(f"failed {chr(65+i)}")
                    my_logging((f_name, directory_name, "failed"))
            
            except:
                logging.info(30*'-')
                logging.exception('')
        
        my_logging(f"{cnt} of 4 worked at {f_name}, temp was {check_temp()} deg.\n")
        camera.release()
#         for i in range(self.camNum):
#             self.choose_channel(chr(65+i)) 
#             self.camera.release()


def check_temp():
    result = 0.0
    # The first line in this file holds the CPU temperature as an integer times 1000.
    # Read the first line and remove the newline character at the end of the string.
    if os.path.isfile('/sys/class/thermal/thermal_zone0/temp'):
        with open('/sys/class/thermal/thermal_zone0/temp') as f:
            line = f.readline().strip()
        # Test if the string is an integer as expected.
        if line.isdigit():
            # Convert the string with the CPU temperature to a float in degrees Celsius.
            result = float(line) / 1000
    return int(result)

def my_logging(data):
    with open("/home/pi/Desktop/agueda_imgs/log_file1.txt", "a") as logger:
        if len(data)>5:
            logger.write(data)
            
            logger.write(32*"-"+"\n")
        else:
            line = str(data) + "\n"
            logger.write(line)




