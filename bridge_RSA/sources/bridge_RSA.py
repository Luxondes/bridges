#!/usr/bin/env python
import socket
import signal
import struct
import math
import time
import os
import os.path
import sys
from ctypes import *
from RSA_API import *

## Host server which serve to bridge with the RSA and any client.
class HostServer():
    def  __init__(self,center_freq,span,harddisk):
        self.dataSaved=[]
        self.isRunning=False
        self.thread=None
        self.status =None
        self.messageToSend=None
        self.connected=False
        self.connection=None
        self.client_address=None
        self.server_address=None
        self.hostsocket=None
        self.center=c_double(center_freq)
        self.span=span
        self.harddisk=harddisk
        self.att=c_double(0)
        
    ## Stop the host server and disconnect with the RSA
    def stop(self,signum,frame):
        print("Stop the server")
        self.isRunning=False
        self.connected=False
        if(self.rsa!=None):
            self.rsa.DEVICE_Disconnect()
        if(self.connection!=None):
            self.connection.close()
        
        
        

    ## Run on loop the standard protocol for Python connection.
    ## Wait a client. If no client, wait again.
    ## If client, wait commands and answer them.
    def __run(self):
        timeoutcustom=0
        self.isRunning=True
        try:
            self.create_server_socket()
            if not self.isRunning:
                self.hostsocket.close()
                return
            while(self.isRunning):
                # Wait client
                print("Waiting connection")
                self.accept_new_connection()
                timeoutcustom=0
                if self.connected:
                    
                    try:
                        while(self.connected):
                            # Wait command
                            if not self.isRunning:
                                self.close_socket()
                                break
                            try:
                                data=self.connection.recv(4096).decode()
                                if(data==""):
                                    print('Request to close the connection between client and bridge.')
                                    self.close_socket()
                                    pass
                                # Get Command, compute the command.
                                if (data):
                                    self.read_data(data)

                            except socket.timeout:
                                # If too many exception, close the client.
                                timeoutcustom+=1
                                if timeoutcustom > 5:
                                    self.close_socket()

                            except socket.error:
                                self.close_socket()
                                pass
                    finally:
                        print("The connection between the bridge and the client has be closed.")
                        self.close_socket()
        finally:
            print("The bridge has be closed.")
            self.hostsocket.close()
            self.hostsocket=None
            self.isRunning=False

    ## Create the server socket on the PC (This code work for Linux too but RSA.dll is windows-only)
    ## The socket will be on the ip of the PC and the port choosen.
    def create_server_socket(self):
        self.server_address=("0.0.0.0",9001)
        #Scanphone cannot read the port 9003 or 9002, only 9001. Console can do it if written on the input
        self.hostsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.hostsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

        try:
            self.hostsocket.bind(self.server_address)
        except:
            self.isRunning=False

        # If the port are not available, shutdown the script.
        if not self.isRunning:
            self.hostsocket.close()
            return
        ip,port=self.hostsocket.getsockname()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            print("External IP of the computer: "+s.getsockname()[0])
            s.close()
        except:
            print("External IP of the computer not found")

        print("Bridge port: "+str(port))
        
        self.server_address=self.hostsocket.getsockname()
        if not self.isRunning:
            self.hostsocket.close()
            return
        self.hostsocket.settimeout(5)
        self.hostsocket.listen(5)

    ## Wait a new connection for "self.hostsocket.listen(value)" seconds. Declared on create_server_socket()
    def accept_new_connection(self):
        try:
            self.connection, self.client_address = self.hostsocket.accept()
            self.connection.settimeout(10)
            print("Accepting new connection")
            self.connected=True
        except socket.timeout:
            self.connected=False
            return

    ## Compute the command. A command ends with a \n but can receive some part of the command so check that.
    ## When a \n has be detected, merge all data for each command on it (ex: command\ncommand\n)
    def read_data(self,data):
        self.dataSaved+=[data]
        # Check if the data contain a \n
        if('\n' in data):
            message=""
            # Merge all data
            for dat in self.dataSaved:
                message=message + dat
            self.dataSaved=[]
            splits=message.split("\n")
            # Split the merged data to multi commands then read each command and return the answer to the client.
            for i in range(0,len(splits)-1):
                answer=self.readAndReturn(splits[i].strip().upper())
                if(answer != None):
                    self.connection.send(answer)

    ## Close the socket.
    def close_socket(self):
        if self.connection!=None :
            self.connection.close()
            self.dataSaved=[]
        self.connected=False

    ## Init answer of each commands then run the host server.
    ## On the fast_RSA, load the RSA library then compute all commands needed.
    ## The RSA is a C library and we use the ctypes for convert these C functions to Python functions.
    ## You can found theses functions on the internet.
    def init(self):
        # Load DLL into memory.
        dll_name="RSA_API.dll"
        # Need the RSA installed on this location.
        os.add_dll_directory(self.harddisk+":\\Tektronix\\RSA_API\\lib\\x64")
        self.rsa = cdll.LoadLibrary(dll_name)

        numFound = c_int(0)

        intArray = c_int * DEVSRCH_MAX_NUM_DEVICES
        deviceIDs = intArray()
        self.deviceSerial = create_string_buffer(DEVSRCH_SERIAL_MAX_STRLEN)
        self.deviceType = create_string_buffer(DEVSRCH_TYPE_MAX_STRLEN)
        apiVersion = create_string_buffer(DEVINFO_MAX_STRLEN)

        self.rsa.DEVICE_GetAPIVersion(apiVersion)
        print('API Version {}'.format(apiVersion.value.decode()))

        self.err_check(self.rsa.DEVICE_Search(byref(numFound), deviceIDs,
                                self.deviceSerial, self.deviceType))
        if numFound.value < 1:
            print('No instruments found. Exiting script.')
            return
        else:
            print('Device type: {}'.format(self.deviceType.value.decode()))
            print('Device serial number: {}'.format(self.deviceSerial.value.decode()))
            self.err_check(self.rsa.DEVICE_Connect(deviceIDs[0]))

        self.specSet = self.config_spectrum()

        # At the end, run the thread of the host server.
        self.__run()
        return True

    def err_check(self,rs):
        if ReturnStatus(rs) != ReturnStatus.noError:
            raise RSAError(ReturnStatus(rs).name)

    def isRunning(self):
        return self.isRunning

    ## RSA can return 5 types of unit, we convert the int answer to string answer.
    def getUnit(self):
        if(self.specSet.verticalUnit==0):
            return "DBM"
        if(self.specSet.verticalUnit==1):
            return "W"
        if(self.specSet.verticalUnit==3):
            return "A"
        if(self.specSet.verticalUnit==4):
            return "DBMV"
        return "V"

    ## Recept the command, see if he has a question mark (so a GET command) else this is a SET command.
    ## Then switch on each case and return the answer.
    def readAndReturn(self,message):
        if("?" in message):
            # GET command
            if(message == "*IDN?"):
                # IDN used for the xml. A universal IDN is "Luxondes Simu,numero,version" but need to use the commands on the simulation.py from fast_simulation
                # Or you can create the xml then put the xml on CONFIG_SCPI folder of the folder Luxondes of your phone.
                return self.encode(self.deviceType.value.decode()+"_"+self.deviceSerial.value.decode())
            if(message == "TRACE?"):
                # Get the trace then return it (ex: val1,val2,val3). On this case, a list of float without any comma but with a header containing the number of float
                return self.trace()
            if(message == "UNIT?"):
                # Return a string containing the unit.
                return self.encode(self.getUnit())
            if(message == "START?"):
                # Return a string containing the start.
                return self.encode(str(self.center.value-self.specSet.span/2))
            if(message == "STOP?"):
                # Return a string containing the stop.
                return self.encode(str(self.center.value+self.specSet.span/2))
            if(message == "CENTER?"):
                # Return a string containing the center.
                return self.encode(str(self.center.value))
            if(message == "SPAN?"):
                # Return a string containing the span.
                return self.encode(str(self.specSet.span))
            if(message == "ATT?"):
                # Return a string containing the attenuation (Do not affect Console or Scanphone).
                return self.encode(str(self.att.value))
            if(message == "RBW?"):
                # Return a string containing the RBW (Do not affect Console or Scanphone).
                return self.encode(str(self.specSet.rbw))
            if(message == "VBW?"):
                # Return a string containing the VBW (Do not affect Console or Scanphone).
                return self.encode(str(self.specSet.vbw))
        else:
            # SET command
            splits=message.split(" ")
            if(splits[0] == "CENTER"):
                # Set the center of the RSA. Then Get it again on the case or the center is not applied.
                self.rsa.CONFIG_SetCenterFreq(c_double(int(splits[1])))
                self.rsa.CONFIG_GetCenterFreq(byref(self.center))
                return None
            # Because set span modify the rbw so the number of points on the array, we cannot modify the span.
##            if(splits[0] == "SPAN"):
##                # Set the span of the RSA.
##                self.span=int(splits[1])
##                self.setSpan(self.specSet,self.span)
##                self.rsa.SPECTRUM_SetSettings(self.specSet)
##                self.rsa.SPECTRUM_GetSettings(byref(self.specSet))
##                return None
        return None

    ## Add \n at the end of the message then transform it to a array of bytes.
    def encode(self,mes):
        return (mes+"\n").encode()

    ##  Get data from RSA.
    def acquire_spectrum(self):
        ready = c_bool(False)
        traceArray = c_float * self.specSet.traceLength
        traceData = traceArray()
        outTracePoints = c_int(0)
        traceSelector = SpectrumTraces.SpectrumTrace1

        self.rsa.DEVICE_Run()
        self.rsa.SPECTRUM_AcquireTrace()
        while not ready.value:
            self.rsa.SPECTRUM_WaitForDataReady(c_int(100), byref(ready))
        self.rsa.SPECTRUM_GetTrace(traceSelector, self.specSet.traceLength, byref(traceData),
                              byref(outTracePoints))
        self.rsa.DEVICE_Stop()
        return traceData

    ## Get the data from RSA then convert it to a readable format for the client.
    ## Create a header begin with a # then the length of the number of value followed per the number of value.
    ## Ex: # + 4 + 1803
    def trace(self):
        values=self.acquire_spectrum()
        lengthofLine=str(self.specSet.traceLength*4)
        text=("#"+str(len(lengthofLine))+lengthofLine).encode()
        for i in values:
            text+=bytearray(struct.pack("f",i))

        text+="\n".encode()
        return text

    ## Set the span, but set also the rbw for be a ratio 100 of the span.
    def setSpan(self,specSet,span):
        specSet.span = c_double(span)
        value=(span/100.0)/5.
        leng=(10**(len(str(value))-3))
        value=math.floor(value/leng)*5*leng
        specSet.rbw = c_double(value)
        
    ## Get the settings of the RSA.
    def config_spectrum(self):
        self.rsa.SPECTRUM_SetEnable(c_bool(True))
        self.rsa.CONFIG_SetAutoAttenuationEnable(c_bool(True))
        self.rsa.SPECTRUM_SetDefault()
        specSet = Spectrum_Settings()
        self.rsa.SPECTRUM_GetSettings(byref(specSet))
        self.rsa.CONFIG_SetCenterFreq(self.center)
        self.setSpan(specSet,self.span)
        specSet.verticalUnit = SpectrumVerticalUnits.SpectrumVerticalUnit_dBm
        self.rsa.SPECTRUM_SetSettings(specSet)
        self.rsa.SPECTRUM_GetSettings(byref(specSet))
        return specSet

## read all variables inside the file properties.txt.
def readPropertiesFile():
    # Default values
    values = [106.6e6,10e6,'C']
    
    bol=os.path.isfile('./properties.txt')
    if not bol:
        return values
    print("This server bridge will use the properties.txt")

    file1 = open('./properties.txt', 'r')
    lines = file1.readlines()



    # Read each line.
    for val in lines:
        if(val.startswith("#")):
            continue
        if(val.startswith("center=")):
            val=val[len("center="):]
            try:
                values[0]=float(val)
            except:
                None
        if(val.startswith("span=")):
            val=val[len("span="):]
            try:
                values[1]=float(val)
            except:
                None
        if(val.startswith("harddisk=")):
            val=val[len("harddisk="):]
            try:
                values[2]=str(val).strip()
            except:
                None
    return values

## Launch the host server and link the CTRL+D (stop) and CTRL+Q (quit) with the stop of the server.
if __name__ == '__main__':
    values=readPropertiesFile()
    print("Center: "+str(values[0])+"Hz Span: "+str(values[1])+"Hz")

    hostserver=HostServer(values[0],values[1],values[2])

    signal.signal(signal.SIGTERM,hostserver.stop)
    signal.signal(signal.SIGINT,hostserver.stop)
    hostserver.init()
