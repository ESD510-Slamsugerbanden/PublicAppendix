import socket
import struct
import time

from pynput.mouse import Controller
import logging
import serial

####################
# Interface for the ESP32 via UDP
####################


class UdpProtocolClient:
    def __init__(self, host="192.168.4.1", port=8700, timeout=2.0):
        """
        UDP interface for ESP32 protocol.
        host: ESP32 IP (default 192.168.4.1 if ESP32 is AP)
        port: UDP port (default 4210)
        timeout: socket timeout for receive
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def set_pos(self, azimuth: float, elevation: float):
        """
        Send a command packet with azimuth/elevation.
        """
        packet = struct.pack("<BBff", 0x42, 0x01, azimuth, elevation)
        self.sock.sendto(packet, (self.host, self.port))

    def get_pos(self):
        """
        Wait for a response packet.
        Returns (azimuth, elevation) as floats.
        """
        self.sock.sendto(bytes([0x42, 0x02]), (self.host, self.port))


        try:
            data, _ = self.sock.recvfrom(1024)
        except socket.timeout:
            logging.error("UDP socket timeout")
            return None, None


        if len(data) != 8:
            logging.error("Invalid packet length recieved")
            return None, None

        az, el = struct.unpack("<ff", data[:8])

        return az, el



class ez_comm:
    def __init__(self, device: str):
        self.serial = serial.Serial(device, 115200, timeout=10)

    def get_pos(self):
        self.serial.flush()

        self.serial.write(bytes("AZ EL\n", encoding="ascii"))
        time.sleep(0.01)
        buffer = self.serial.read_all()
        buffer = buffer.strip()
        split = buffer.split(b" ")
        azimuth = float(split[0][2:])
        elevation = float(split[1][2:])

        return (azimuth, elevation)


    def set_pos(self, azimuth: float, elevation: float):
        msg = "AZ{:.1f}\n".format(azimuth)
        self.serial.write(bytes(msg, encoding="ascii"))
        msg2 = "EL{:.1f}\n".format(elevation)
        self.serial.write(bytes(msg2, encoding="ascii"))
        

    def set_zero(self):
        msg = "ZA \n"
        self.serial.write(bytes(msg, encoding="ascii"))

        response = self.serial.readline()
        #msg2 = "ZE"
        #self.serial.write(bytes(msg2, encoding="ascii"))
        if(response == 'OK\n'):
            return True
        
        return Falsec

if __name__ == "__main__":

    import switch as sw
    sw.set_switch(3)
    #client = UdpProtocolClient("192.168.4.1", 8700)
    tarm = ez_comm("/dev/ttyUSB0")
    #tarm.set_zero()


    mouse = Controller()
    while(True):
        ms = time.time()
        x, y = mouse.position 
        azi = (x/1920)*2-1
        ele = (y/1080)*2-1 

        print(azi, ele)
        #print(client.get_pos())
        #client.set_pos(float(azi)*45, (float(ele)*45) -90)


        tarm.set_pos(90*azi, 60*ele+3)
        tarm.get_pos()
        time.sleep(0.01)  
