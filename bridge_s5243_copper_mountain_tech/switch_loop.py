"""
Test script for ordering the correlator to do a sweep with specified parameters
Date 04/12/2021
"""

import serial

nb_common_ports = 4
nb_ports = 10


class Switch():
    def  __init__(self):
        # First connect the device to the computer
        # You can list available ports the the following command: "python -m serial.tools.list_ports"
        # The default configuration is: 9600, 8, N, 1,no timeout, we could specify but configuring the baudrate is enough
        self.correlator = serial.Serial('COM3', 100000)



    def close(self):
        self.correlator.close()

    def select_port(self,common, port):
        common_str = str(common)
        port_str = str(port)
        # Check if we must add a '0'
        if port < 10:
            return('S' + common_str + '0' + port_str)
        else:
            return('S' + common_str + port_str)


