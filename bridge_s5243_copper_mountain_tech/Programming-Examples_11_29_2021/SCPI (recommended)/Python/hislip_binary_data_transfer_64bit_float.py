# -*- coding: utf-8 -*-
"""
Created on 5/21/2021

OVERVIEW:
    This example demonstrates binary data transfer with 64-bit float format through TCP/IP Hislip.
    RVNA and TRVNA DO NOT support hislip

Before running the code:
    1. Make sure VNA software is running
    2. Go to system -> Misc setup -> network remote settings -> turn on socket server
    3. make sure socket server is 5025

Additional information:
    1. The SCPI programming manual is intalled with the VNA software. By default:
        C:\VNA\S2VNA or S4VNA\Doc
    
"""

import pyvisa

#rm = pyvisa.ResourceManager('@py') # do not use, pyvisa-py does not work with hislip
rm = pyvisa.ResourceManager('C:/WINDOWS/system32/visa32.dll')  # use ni visa 32 bit as backend, must install NI VISA
#rm = pyvisa.ResourceManager('C:/WINDOWS/system32/visa64.dll')  # use ni visa 64 bit as backend, must install NI VISA

#Connect to a Socket on the local machine at 5025
try:
    # 127.0.0.1 is the local loopback IP address. Don't change this IP address if 
    # the VNA is connected to the same PC which runs this code
    CMT = rm.open_resource('TCPIP0::127.0.0.1::hislip0::INSTR')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
# Do not set the read_termination because Hislip does not use termination character

#Set a really long timeout period for slow sweeps
CMT.timeout = 10000

###########################################
###########################################
###### SCPI commands start here ###########
###########################################
###########################################

# set trigger source to bus
CMT.write("TRIG:SOUR BUS")

# select binary data format
CMT.write('FORM:DATA REAL') # 64 bit float

# select binary data endianess 
# NORM means big endian format
# SWAP means little endian format
CMT.write('FORM:BORD SWAP')
CMT.query('*OPC?')

# trigger the VNA to make one sweep
CMT.write('TRIG:SING')
CMT.query('*OPC?')

# select trace 1 and read log mag data
CMT.write('CALC1:PAR1:SEL')
logmag = CMT.query_binary_values('CALC1:DATA:FDAT?',datatype='d') # is_big_endian attribute is false by default
logmag = logmag[::2]
print(logmag)

# set trigger source back to internal
CMT.write("TRIG:SOUR INT")






