#%%

from datetime import datetime




def logger_func(log_path, values):
    with open(log_path, 'a') as f:
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ## time, pixel_value, temp_value , img_name
        f.write(f"{time}, {values[0]}, {values[1]}, {values[2]}\n")
        
def init_log(log_path):
    with open(log_path, 'w') as f:
        f.write("time, pixel_value, temp_value\n")



#%% MARK: for testing
if __name__ == "__main__":
    #%% 
    import numpy as np

    mean_pixel_value = 128
    std_dev_pixel_value = 10
    time = np.arange(0, 10, 0.1)

    mock_pixel_values = np.random.normal(loc=mean_pixel_value, 
                                        scale=std_dev_pixel_value, 
                                        size=len(time)).astype(int)

    mock_temp_values = np.random.normal(loc=mean_pixel_value-50, 
                                        scale=std_dev_pixel_value, 
                                        size=len(time)).astype(int)



    log_path = r"C:\Users\Roni\Desktop\Roni_new\python scripts\pavlovian sunflowers\operant-project\mock_exp\2025-05-13\mock_log.txt"
    init_log(log_path)

    for i in range(len(mock_pixel_values)):
        values=(mock_pixel_values[i], mock_temp_values[i], f"img_{i}.jpg")
            
        logger_func(log_path, values)

