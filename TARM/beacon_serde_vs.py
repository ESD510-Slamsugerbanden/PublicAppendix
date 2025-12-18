import threading
import socket
import numpy as np
import struct




class Beacon_decoder:
    def __init__(self, port=8700):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4096)  # 4 KB
        self.sock.setblocking(True)  # ensures it's blocking


        self.sock.bind(("127.0.0.1", port))
        self.last_corr = np.zeros(4)
        self.last_rssi = np.zeros(4)
        self.thread_handle = threading.Thread(target=self._runner)
        self.ready_flag = False

    def _runner(self):
        while(True):
            data, addr = self.sock.recvfrom(9*4)
            buffer = struct.unpack("fffffffff", data)
            self.last_corr = buffer[:4]
            self.last_rssi = buffer[4:8]
            self.lock_counter = buffer[8]
            self.ready_flag = True




    def begin(self):
        self.thread_handle.start()

    def flush(self):
        self.ready_flag = False
    def avaliable(self):
        return self.ready_flag

    def get_values(self):
        self.ready_flag = False
        return (self.last_rssi, self.last_corr)
    
