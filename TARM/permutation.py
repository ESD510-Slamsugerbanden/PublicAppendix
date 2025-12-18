
import filters as flt





##The wiggle controller doing permutation
class permutation_controller:
    def __init__(self, T_s, start_theta):
        self.w_n = 1.4*np.pi
        self.highpass = flt.Highpass(self.w_n, T_s)
        self.lowpass = flt.Lowpass(self.w_n, T_s)
        self.hp_theta = flt.Highpass(self.w_n, T_s)
        self.lp_theta  = flt.Lowpass(self.w_n*8, T_s)
        self.T_s = T_s
        self.permu_A = np.deg2rad(10) #How big should the permutation be in radians
        self.ki = 3
        self.ki2 = 0
        self.w_per = 2*np.pi
        self.probe_counter = 0
        self.theta_i = start_theta
        self.theta_i2 = 0
        self.permutation = 0
        self.i_log = []
        self.hp_log = []
        self.last = 0
        pass

    def compute(self, rssi, true_theta):
        d_theta = self.hp_theta.filter(true_theta)
        d_theta = self.lp_theta.filter(d_theta)
        est_perm = np.sin(self.probe_counter * self.T_s * self.w_per - np.deg2rad(20))
        print(d_theta)
        hp_res = self.highpass.filter(rssi)
        temp = self.lowpass.filter(self.T_s * self.permutation   * hp_res * self.ki) 
        self.theta_i += temp
        self.theta_i2 += self.theta_i / self.ki
        self.permutation = self.permu_A * np.sin(self.probe_counter * self.T_s * self.w_per)
        self.probe_counter += 1
        return self.permutation + self.theta_i #+ self.theta_i2 * self.ki2


#andres bibs
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


#vores biblioteker
from Rotax import ez_comm #Uart controller for the motor
from beacon_serde_vs import Beacon_decoder
import switch as sw


if __name__ == "__main__":
    tarm = ez_comm("/dev/ttyUSB0") #controller for the arm
    beacon_decoder = Beacon_decoder(my_id=1) #Sets up a decoder looking for the given ID
    beacon_decoder.start() #starts the decoder in the background
    theta_max = 200
    theta_min = 100
    theta_start = 250 

    tarm.set_pos(0, theta_start)
    T_s = 1/(256) * 8
    sw.set_switch(2)
    
    ctrl = permutation_controller(T_s, np.deg2rad(theta_start))

    while(True):
        if(beacon_decoder.avaliable()):
            rssi, corr = beacon_decoder.get_lastest()   
            azi,ele = tarm.get_pos()
            theta = np.rad2deg(ctrl.compute(rssi, np.deg2rad(ele)))
            
            
            #theta = min(theta, theta_max)
            #theta = max(theta, theta_min)
            #ctrl.theta_i = min(ctrl.theta_i, np.deg2rad(theta_max))
            #ctrl.theta_i  = max(ctrl.theta_i, np.deg2rad(theta_min))
            if theta != float('nan'):
                tarm.set_pos(0, theta)
            print("RSSI {:.2f},\t Theta: {:.2f}\t DIR:{:.2f} \n".format(rssi, theta, ctrl.theta_i))
