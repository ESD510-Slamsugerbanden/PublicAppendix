
import numpy as np
from gnuradio import gr
from gnuradio import gr
import pmt
import socket as sock
import struct




class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, Port=8700):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='MSQ UDP sink',   # will show up in GRC
            in_sig=[],
            out_sig=[]
        )
        self.message_port_register_in(pmt.intern("MSG in"))

        #Sets up message port
        self.port = Port
        self.set_msg_handler(pmt.intern("MSG in"), self.handle_msg)
        #Sets up socket for passing on the RSSI values
        self.sock = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
        


    def handle_msg(self, msg):
        if pmt.is_dict(msg):
            
            keys = ["CH0", "CH1", "CH2", "CH3"]
            ch = np.zeros(4, dtype=np.float32)
            
            keys = ["RSSI0", "RSSI1", "RSSI2", "RSSI3"]
            rssi = np.zeros(4, dtype=np.float32)


            buf = bytes()
            for i in range(len(keys)):
                ch[i] = pmt.dict_ref(msg, keys[i], pmt.PMT_NIL)
                buf += struct.pack("f", ch[i])
            
            for i in range(len(keys)):
                rssi[i] = pmt.dict_ref(msg, keys[i], pmt.PMT_NIL)
                buf += struct.pack("f", rssi[i])


            locks = pmt.dict_ref(msg, "Locks", pmt.PMT_NIL)
            buf += struct.pack("f", ch[i])            
            print(f"Send UDP package len={len(buf)}")
            self.sendto(buf, ("127.0.0.1", self.port))

        pass


    def work(self, input_items, output_items):
        """example: multiply with constant"""
        
        
        
        
        
        return len(output_items[0])
