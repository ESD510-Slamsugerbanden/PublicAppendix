#andres bibs
import numpy as np
import matplotlib.pyplot as plt
import time

from angle_corr import get_rssi ##Simulated RSSI response
import atexit

import pandas as pd
import RPi.GPIO as GPIO

#from Temp_init_search import search_initial_location


list_angle = []
list_time = []
list_rssi = []
list_pos = []

def exit_handler():
    dataframe = pd.DataFrame(({'Angles':list_angle,'Times':list_time, 'RSSI':list_rssi,'POS':list_pos}))
    dataframe.to_csv(f"{time.time()}.csv")
    



class lp_server:


    def __init__(self, w_n, T_s_back):
        import threading
        self.filter = flt.Lowpass(w_n, T_s_back)
        self.T_s = T_s_back
        self.tarm = ez_comm("/dev/ttyUSB0")
        self.thread_handle = threading.Thread(target=self._internal_runner)
        self.pos = self.tarm.get_pos()[0]
        self.start_el = -30

    def start(self):
        self.thread_handle.start()

    def set_pos(self, azimuth: float, elevation: float):
        self.pos = azimuth
        
    

    def get_pos(self):
        return self.tarm.get_pos()

    def _internal_runner(self):
        while True:
            flt = self.filter.filter(self.pos)
            self.tarm.set_pos(flt,  self.start_el )
            time.sleep(self.T_s)


    def getpos(self):
        return self.tarm.get_pos()

#vores biblioteker
from Rotax import ez_comm #Uart controller for the motor
import filters as flt


def get_correlation(samples, lookup):
    """Gets the index for max correlation between the two bitches"""
    max_score = -np.inf
    max_i = 0
    corr_scores = [0]*len(lookup)
    window = np.hanning(len(lookup))/20 + np.ones(len(lookup))

    for i in range(len(lookup)):
        res = lookup[i]* samples
        corr_scores[i] = np.sum(res)
    corr_scores = corr_scores * window
    return np.argmax(corr_scores), corr_scores


def get_vector(beacon_decoder):
    rssi = [0, 0, 0, 0]
    for i in range(4):
        sw.set_switch(i)
        beacon_decoder.flush()
        while(beacon_decoder.avaliable() == False):
            pass

        beacon_decoder.flush()
        while(beacon_decoder.avaliable() == False):
            pass
        rssi[i], corr = beacon_decoder.get_lastest()
    return rssi


def get_calibration_vector(n, scanwidth, elevation):
    beacon_decoder = Beacon_decoder(my_id=1) #Sets up a decoder looking for the given ID
    beacon_decoder.start() #starts the decoder in the background
    tarm = ez_comm("/dev/ttyUSB0")
    tarm.set_pos(0, elevation)
    print("Point TARM towards source")
    name = input()
    print("starting calibration")
    sim_results, theta_array = get_sim_vectors(n, scanwidth)
    tarm.set_pos(np.rad2deg(theta_array[0]), elevation)
    
    errors = []
    for i in range(len(theta_array)):
        tarm.set_pos(np.rad2deg(theta_array[i]), elevation)
        while(np.abs(tarm.get_pos()[0] - np.rad2deg(theta_array[i])) > 5):
            pass
        rssi = get_vector(beacon_decoder)
        rssi = rssi / np.linalg.norm(rssi)
        errors.append(rssi / sim_results[i])
    

    plt.plot(theta_array, errors)
    plt.show()




from beacon_serde_vs import Beacon_decoder 

def get_sim_vectors(n, scanwdith):
    sim_results = [[float,float,float,float]]*n
    theta_array = np.linspace(-scanwidth, scanwidth, n)
    for i in range(n):
        sim_results[i] = np.abs(get_rssi(theta_array[i]))
        sim_results[i] = np.divide(sim_results[i], np.sqrt(np.sum(np.square(sim_results[i]))))#np.divide(sim_results[i], np.sum(sim_results[i]))
        #sim_results[i] = sim_results[i] - np.arange(4)*np.mean(sim_results[i]) 
    return sim_results, theta_array



if __name__ == "__main__":
    
    atexit.register(exit_handler)
    scanwidth = np.deg2rad(60)
    n = 30
    sim_results, theta_array = get_sim_vectors(n, scanwidth)
    ##Calulates fixed possible simulated results
    #get_calibration_vector(n, scanwidth, 30)
    
    decoder = Beacon_decoder(port=8700)
    decoder.begin()

    tarm = lp_server(6.28*12, 0.05)
    tarm.start()

    

    azimuth = 0
    #azimuth,_ = search_initial_location() 
    t_last = time.time()

    plt.ion()
    beam_offsets = [48, 15, -15, -48]
    fig = plt.figure()
    regnbue = ['r', 'g', 'b', 'm']
    ax = fig.add_subplot()
    line = ax.plot([], [])
    line2 = ax.plot([], [])
    line3 = ax.plot([], [])
    line4 = ax.plot([], [])
    ax.set_ylim(-2,2)
    ax.set_xlim(min(beam_offsets)-10, max(beam_offsets)+10)

    w_n = 1*2*np.pi
    T_s = 1/4
    est_pos  = azimuth
    #print(line)
    T_s = 1/5
    k_i = 1.5
    
    rssi = [0]*4

    decoder.flush()
    while(True):
        while(decoder.avaliable() == False):
            pass
            plt.pause(0.01)
        rssi, corr = decoder.get_values()
        rssi_norm =rssi/np.linalg.norm(rssi)
        i_theta, scores = get_correlation(rssi_norm, sim_results)
        azimuth += T_s * k_i * (np.rad2deg(theta_array[i_theta]))

        
        tarm.set_pos(azimuth, 00)
        t_now = time.time()
        list_rssi.append(rssi)
        list_angle.append(theta_array[i_theta])
        list_pos.append(tarm.get_pos()[0])
        list_time.append(t_now)
        print("Ts: {:.3f}, azi: {:.2f}".format(t_now - t_last, azimuth))
        t_last = t_now
        line[0].set_data(beam_offsets, rssi_norm)
        line2[0].set_data(beam_offsets, sim_results[i_theta])
        line3[0].set_data(np.linspace(-np.rad2deg(scanwidth), np.rad2deg(scanwidth), len(scores)), scores)
        target_angle = np.rad2deg(theta_array[i_theta])
        line4[0].set_data([target_angle,target_angle], [-1, 40])
        pass
