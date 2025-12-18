import numpy as np
from gnuradio import gr
import pmt
import uhd
from numba import njit
import RPi.GPIO as GPIO



Pin1 = 17
Pin2 = 27
Pin_led = 0



###Functions that handles 
def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Pin1, GPIO.OUT)
    GPIO.setup(Pin2, GPIO.OUT)
    GPIO.output(Pin1, GPIO.LOW)
    GPIO.output(Pin2, GPIO.LOW)
    GPIO.setup(Pin_led, GPIO.OUT)
    GPIO.output(Pin_led, GPIO.LOW)


def set_switch(sw):
    
    match sw:
        case 1:
            GPIO.output(Pin1, GPIO.LOW)
            GPIO.output(Pin2, GPIO.LOW)
        
        case 0:
            GPIO.output(Pin1, GPIO.HIGH)
            GPIO.output(Pin2, GPIO.LOW)
        
        case 3:
            GPIO.output(Pin1, GPIO.LOW)
            GPIO.output(Pin2, GPIO.HIGH)
        

        case 2:
            GPIO.output(Pin1, GPIO.HIGH)
            GPIO.output(Pin2, GPIO.HIGH)



#Kernel for 

@njit
def numba_kernel(input, buffer, mycode, corr_thres):
    N = len(input)
    output = np.empty(N, dtype=np.float32) #Preallocate array

    i_maxcorr = -1
    maxcorr = 0.0
    peakflag = False

    for i in range(N):
        for k in range(len(buffer)-1, 0, -1):
            buffer[k] = buffer[k-1]
        buffer[0] = input[i]

        corr = np.dot(buffer, mycode) / len(buffer)

        output[i] = corr

        val = abs(corr)
        if val > corr_thres:
            maxcorr = corr
            i_maxcorr = i
            peakflag = True

    return output, peakflag, maxcorr, i_maxcorr



SW0 = 0x10
SW1 = 0x20
SW2 = 0x40
SW3 = 0x80


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, burst_period=100,bursts = 4, gold_code=1, sps=3, minislot_delay=50, correlation_threshold=0.05):  # only default arguments here
        """Jydesnak DE-beaconizer"""
        gr.sync_block.__init__(
            self,
            name='Jydesnak DE-BEACONIZER',   # shows up in GRC
            in_sig=[np.float32, np.float32],
            out_sig=[np.float32],
        )
        self.message_port_register_out(pmt.intern("Corr OUT"))
        self.burst_period = burst_period ##How often we expect the beacon to repeat itself
        self.bursts = bursts #How many bursts we expect pr beacon
        self.sps= sps #Samples per symbol
        self.mycode = np.subtract(np.repeat(PLACEHOLDER_CODEVECTOR(id), self.sps) * 2 , 1)##Genererer vores SCHLONG vektor der kan bruges
        self.mycode = np.flip(self.mycode) #FLips to match what we expect in out buffer
        self.vectorlength = len(self.mycode) #Length of the vector in samples
        self.buffer = np.zeros(self.vectorlength, dtype=np.float32)
        self.correlation_threshold = correlation_threshold
        self.maxcorr = 0
        self.i_maxcorr = 0
        self.rssi_buffer = np.zeros(int(self.vectorlength*1.2), dtype=np.float32)
        self.rssi_est_buffer = np.zeros(4, dtype=np.float32)
        
        
        ###STUFF for locking onto our target in time
        self.minislot = int(self.vectorlength/4)
        self.set_max_output_buffer(0, self.minislot)
        self.T_search = int(self.minislot*6) 
        self.switch_number = 0
        self.usrp = None
        self.cooldown = 0 
        self.minislot_delay = minislot_delay
        self.locks = 0
        self.corrbuffer = np.zeros(4)    


    def start(self):
        print(f"[DE-beaconizer]: minislot: {self.minislot}, \t burst period: {self.burst_period}")
        # trigger JIT compile
        numba_kernel(np.zeros(1, np.float32),
                     self.buffer,
                     self.mycode,
                     self.correlation_threshold)
        self.usrp = uhd.usrp.MultiUSRP() ##Finder den første og den bedste USRP
        self.usrp.set_gpio_attr("FP0", "DDR", 0xFF, 0xF0) ##Sætter alle GPIO'er som output
        self.usrp.set_gpio_attr("FP0", "CTRL", 0x00, 0xF0)

        setup()
        set_switch(1)
        return True

    def work(self, input_items, output_items):
        #The input items to process
        inp = input_items[0]
        out = output_items[0]
        N = len(out)

        #Number of samples to be shifted in our buffer for use in RSSI estimation
        rssi_len = len(input_items[1])


        #Shift into our RSSI buffer
        self.rssi_buffer = np.roll(self.rssi_buffer, rssi_len)
        self.rssi_buffer[:rssi_len] = input_items[1]



        # Call compiled kernel
        output, peakflag, maxcorr, i_maxcorr = numba_kernel(
            inp, 
            self.buffer,
            self.mycode,
            self.correlation_threshold
        )

        out[:] = output

        self.cooldown -= N

        # Handle tagging
        if peakflag and self.cooldown <= 0:
            set_switch((self.switch_number + 1) % 4)


            #Software debounce to ensure one correlation pr code
            self.cooldown = self.vectorlength / 2

            #Shifts the last correlation into our 4-size correlation buffer
            self.corrbuffer = np.roll(self.corrbuffer,  1)
            self.corrbuffer[0] = maxcorr
            

            #Mark the point where the correlations was best.
            key   = pmt.intern("suspekt")
            value = pmt.from_float(maxcorr)
            offset = self.nitems_written(0) + int(i_maxcorr)
            self.add_item_tag(0, offset, key, value)
            key   = pmt.intern("SW")
            value = pmt.from_long(int(self.switch_number))
            offset = self.nitems_written(0) + int(N)
            self.add_item_tag(0, offset, key, value)
            
            ###### Get our RSSI estimate
            self.rssi_est_buffer = np.roll(self.rssi_est_buffer, 1)
            self.rssi_est_buffer[0] = np.sum(self.rssi_buffer)
            


            #Presumed start of tracking signal
            if(self.switch_number == 0):
                #Sets flag to indicate to traffic allowed
                GPIO.output(Pin_led, GPIO.HIGH)
                
                #Handle tags for debugging
                key   = pmt.intern("TRIG")
                value = pmt.from_long(int(self.locks))
                offset = self.nitems_written(0) + int(N)
                self.add_item_tag(0, offset, key, value)
                

                #Add score if the switches were lined up.
                if np.all(np.multiply(self.corrbuffer, [1, -1, -1, 1]) > 0):
                    self.locks += 1
                else:
                    self.locks = 0

            #if we are at the last switch and we have had 5 successful syncs upto that point
            if(self.switch_number == 3 and self.locks > 5):
                #Last part of the message, indicates that user can transmit
                GPIO.output(Pin_led, GPIO.LOW)
                

                pmt_msg = pmt.make_dict()
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("CH0"), pmt.from_float(float(self.corrbuffer[0])))
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("CH1"), pmt.from_float(float(self.corrbuffer[1])))
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("CH2"), pmt.from_float(float(self.corrbuffer[2])))
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("CH3"), pmt.from_float(float(self.corrbuffer[3])))
                
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("RSSI0"), pmt.from_float(float(self.rssi_est_buffer[0])))
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("RSSI1"), pmt.from_float(float(self.rssi_est_buffer[1])))
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("RSSI2"), pmt.from_float(float(self.rssi_est_buffer[2])))
                pmt_msg = pmt.dict_add(pmt_msg, pmt.intern("RSSI3"), pmt.from_float(float(self.rssi_est_buffer[3])))
                
    
                pmt_msg = pmt.dict_add(
                    pmt_msg,
                    pmt.intern("Locks"),
                    pmt.from_float(float(self.locks))
                )
                #outputs the dictionary of correlations and RSSI
                self.message_port_pub(pmt.intern("Corr OUT"), pmt_msg)

            #Handle syncronisation
            if(maxcorr < 0 and (self.switch_number == 2 or self.switch_number == 3)):
                self.switch_number = (self.switch_number +1) % 4
            if(maxcorr > 0 and (self.switch_number == 0 or self.switch_number == 1)):
                self.switch_number = (self.switch_number +1) % 4

        #The actual number of samples processed
        return N