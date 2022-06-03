# -*- coding: utf-8 -*-
"""
Created on 10/1/2020

OVERVIEW:
    This script takes one S11 measurement every 10 minutes and save the data in .csv
    files under the same directory as this script lies.
    
    The VNA software has to be running always when automating the VNA. The VNA software
    is the driver for the VNA

Before running the code:
    1. Make sure S2VNA software is running
    2. Go to system -> Misc setup -> network remote settings -> turn on socket server
    3. make sure socket server is 5025

Additional information:
    1. The SCPI programming manual is intalled with the VNA software. By default:
        C:\VNA\S2VNA\Doc\
    
"""

import visa    #PyVisa is required along with NIVisa
from time import sleep
import os 


rm = visa.ResourceManager('@py')
#Connect to a Socket on the local machine at 5025
#Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::localhost::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
#The VNA ends each line with this. Reads will time out without this
CMT.read_termination='\n'
#Set a really long timeout period for slow sweeps
CMT.timeout = 10000


###########################################
###########################################
######try stuff here#######################
###########################################
###########################################

CMT.write("TRIG:SOUR BUS\n")
CMT.query("*OPC?\n")

# get the directory where this python script is located, the csv file will be saved in the same folder
file_path = os.path.dirname(os.path.realpath(__file__))
for i in range(100):
    CMT.write("TRIG:SING\n")
    CMT.query("*OPC?\n")
    command = 'MMEM:STOR:FDAT ' + '"' + file_path + '/data' + '{}'.format(i) + '.csv"' + '\n'
    CMT.write(command)
    sleep(600)   # seconds
 
CMT.write("TRIG:SOUR INT\n")



