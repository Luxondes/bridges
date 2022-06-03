# -*- coding: utf-8 -*-
"""
Created on Wed Jan 15 16:32:27 2020

@author: Patrick.l
"""

import pyvisa    #PyVisa is required along with NIVisa
import subprocess
import time 

# Concept:
# The complete calibration process is:
# 1) select cal kit definition
# 2) physically connect the cal kit standards and measure the standards
# 3) select calibration type (full 1 port cal, full 2 port cal, response open cal, response short cal, etc.)
# 4) apply calibration

# When automating standards' measurements, the subclass of each standard must be selected first 
# (this is done using SCPI command "SENS:CORR:COLL:SUBC <number>"). 
# If subclass is not selected, the last selected subclass is used

# connect to VNA software
rm = pyvisa.ResourceManager('@py')  # uses pyvisa-py
#rm = pyvisa.ResourceManager('C:/WINDOWS/system32/visa32.dll')  # uses ni visa 32 bit
#rm = pyvisa.ResourceManager('C:/WINDOWS/system32/visa64.dll')  # uses ni visa 64 bit

#Connect to a Socket on the local machine at 5025
#Use the IP address of a remote machine to connect to it instead
try:
    CMT = rm.open_resource('TCPIP0::127.0.0.1::5025::SOCKET')
except:
    print("Failure to connect to VNA!")
    print("Check network settings")
#The VNA ends each line with this. Reads will time out without this
CMT.read_termination='\n'
#Set a really long timeout period for slow sweeps
CMT.timeout = 10000

###########################################
###########################################
###### send SCPI commands here ############
###########################################
###########################################

# this example selects CMT S911T cal kit
CMT.write("SENS:CORR:COLL:CKIT 30")

print("Connect open standard on port 1")
# select subclass for the standard and collect open standard measurement
CMT.write("SENS:CORR:COLL:SUBC 1")
CMT.write("SENS:CORR:COLL:OPEN 1")

print("Connect short standard on port 1")
# select subclass for the standard and collect short standard measurement
CMT.write("SENS:CORR:COLL:SUBC 1")
CMT.write("SENS:CORR:COLL:SHOR 1")

print("Connect load standard on port 1")
# select subclass for the standard and collect load standard measurement
CMT.write("SENS:CORR:COLL:SUBC 1")
CMT.write("SENS:CORR:COLL:LOAD 1")

print("Connect open standard on port 2")
# select subclass for the standard and collect open standard measurement
CMT.write("SENS:CORR:COLL:SUBC 1")
CMT.write("SENS:CORR:COLL:OPEN 2")

print("Connect short standard on port 2")
# select subclass for the standard and collect short standard measurement
CMT.write("SENS:CORR:COLL:SUBC 1")
CMT.write("SENS:CORR:COLL:SHOR 2")

print("Connect load standard on port 2")
# select subclass for the standard and collect load standard measurement
CMT.write("SENS:CORR:COLL:SUBC 1")
CMT.write("SENS:CORR:COLL:LOAD 2")

print("Connect thru standard between port 1 and port 2")
# select subclass for the standard and collect thru standard measurement
CMT.write("SENS:CORR:COLL:SUBC 2") # the subclass number depends on the cal kit definition.
                                   # this example is selecting unknown thru
CMT.write("SENS:CORR:COLL:THRU 1,2")
CMT.write("SENS:CORR:COLL:THRU 2,1") # must sweep the thru in both directions for full 2 port calibration

# select type of calibration and apply the calibration
CMT.write("SENS:CORR:COLL:METH:SOLT2 1,2")
CMT.write("SENS:CORR:COLL:SAVE")





