from Rotax import ez_comm
from beacon_serde_vs import Beacon_decoder
import numpy as np
import time 
import matplotlib.pyplot as plt
import pandas as pd
import atexit


tarm = ez_comm("/dev/ttyUSB0") #controller for the arm
beacon_decoder = Beacon_decoder() #Sets up a decoder looking for the given ID
beacon_decoder.begin() #starts the decoder in the background
Max_elevation = 60
Min_elevation = 10


list_time = []
list_rssi = []
list_pos = []


def exit_handler():
    dataframe = pd.DataFrame(({'Times':list_time, 'RSSI':list_rssi,'POS':list_pos}))
    dataframe.to_csv(f"{time.time()}.csv")

def elevation_search(angle=0):
    steps = 5
    elestep = np.linspace(0,Max_elevation,steps)
    sum_array = np.zeros(steps)
    for i in range(steps):
        tarm.set_pos(angle,elestep[i])
        while(abs(tarm.get_pos()[1]-elestep[i])>5):
            time.sleep(0.01)
            beacon_decoder.flush()
        while(beacon_decoder.avaliable() == False):    
                time.sleep(0.01)
        sum_array[i] = np.sum(beacon_decoder.get_values())
        

    max_ele_index = np.argmax(sum_array)
    max_ele_angle = elestep[max_ele_index]
    return max_ele_angle



def DnC_search(Vinkel1=30, Vinkel2=60, step=4, max_elevation=0, min_elevation=0, angle=0):
            """Simple step-search (divide-and-conquer flavor):
            1) mål RSSI ved Vinkel1 og Vinkel2
            2) vælg den bedst og step i den retning (op hvis Vinkel2 var bedst, ned hvis Vinkel1 var bedst)
            3) stop når RSSI ikke forbedres eller når vi rammer grænser
            Returnerer (best_elevation, best_rssi).
            """         
            tarm.set_pos(angle, Vinkel1)  
            r1 = np.sum(beacon_decoder.get_values())
            tarm.set_pos(angle, Vinkel2)
            r2 = np.sum(beacon_decoder.get_values())

            if r2 > r1:
                start = Vinkel2
                direction = 1
                best_rssi = r2
            else:
                start = Vinkel1
                direction = -1
                best_rssi = r1

            best_elev = start
            current_elev = start + direction * step
            while min_elevation <= current_elev <= max_elevation:
                r = beacon_decoder.get_lastest()
                if r > best_rssi:
                    best_rssi = r
                    best_elev = current_elev
                    current_elev = current_elev + direction * step
                else:
                    break

            return best_elev, best_rssi



def search_initial_location():
    beam_offsets = np.array([-48, -15, 15, 48])
    RSSI_array = []
    angle_array = []
    tarm.set_pos(0,10) #Antager at vi kun kan elevation 0-90 grader så vi starter lige på 30 grader og +30 efter
    
    
    time.sleep(0.2)
    for angle in np.linspace(0,360,4): #Deler 360 grader op i 4 dele så vi kan gætte os hurtigere frem til den bedste vinkel
        tarm.set_pos(angle,10)
        while(abs(tarm.get_pos()[0]- angle)>5):
            time.sleep(0.01)
            beacon_decoder.flush()
        for i in range(3):
            timer = time.time()
            timeout = 0
            while(beacon_decoder.avaliable() == False):    
                time.sleep(0.01)
                if time.time()-timer >= 1:
                    timeout = 1
                    break
                
            if timeout == 1:
                continue
            RSSI,_ = beacon_decoder.get_values()  
            RSSI_array = np.concatenate([RSSI_array, RSSI])
            angle_array = np.concatenate([angle_array, tarm.get_pos()[0]*np.ones(4) + beam_offsets])
            list_pos.append(tarm.get_pos()[0])
            list_time.append(t_now)
            list_rssi.append(RSSI)  
            #time.sleep(1)
    max_rssi = max(RSSI_array)
    max_index = np.argmax(RSSI_array)
    max_angle = angle_array[max_index]


    tarm.set_pos(max_angle,0) #Sætter antennen til den bedste vinkel fundet vi er kun interesseret i azimuth her
    
    exit_handler()
    plt.scatter(angle_array, RSSI_array)
    plt.show()
    time.sleep(1)

    elevation_angle = elevation_search(max_angle)

    tarm.set_pos(max_angle, elevation_angle)
        
    
    azi_pos = max_angle
    ele_pos = elevation_angle
    
    return azi_pos, ele_pos 









t_now = time.time()
azi_posistion, ele_posistion = search_initial_location()

