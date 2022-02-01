#!/usr/bin/env python
import socket
import signal
import struct
import math
import time
import os
import os.path
import sys
from sadevice.sa_api import *

## Host server which serve to bridge with the SA and any client.
class HostServer():
    def  __init__(self,center_freq,span):
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
        self.center=center_freq
        self.span=span
        self.oldText=None
        self.att=0
        self.rbw=0
        
    ## Stop the host server and disconnect with the SA
    def stop(self,signum,frame):
        print("Stop the server")
        self.isRunning=False
        self.connected=False
        if(self.handle!=None):
            sa_close_device(self.handle)
        
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

    ## Init device then run the host server.
    def init(self):
        print("Login to the spectrum analyzer. Wait qew seconds.")
        self.handle = sa_open_device()["handle"]

        # Configure device
        sa_config_level(self.handle, 0.0)
    
        self.setSpan(self.span)
        sa_config_acquisition(self.handle, SA_MIN_MAX, SA_LOG_SCALE)

        # Initialize
        sa_initiate(self.handle, SA_SWEEPING, 0);
        query = sa_query_sweep_info(self.handle)
        self.sweep_length = query["sweep_length"]
        
        # At the end, run the thread of the host server.
        self.__run()
        return True

    def err_check(self,rs):
        if ReturnStatus(rs) != ReturnStatus.noError:
            raise RSAError(ReturnStatus(rs).name)

    def isRunning(self):
        return self.isRunning

    ## SA can return 5 types of unit, we convert the int answer to string answer.
    def getUnit(self):
        return "DBM"
##        return "V"
    def setSpan(self,span):
        self.span=int(span)
        sa_config_center_span(self.handle, self.center, self.span)
        self.rbw=(self.span/100.0)/5.
        leng=(10**(len(str(self.rbw))-3))
        self.rbw=math.floor(self.rbw/leng)*5*leng
        sa_config_sweep_coupling(self.handle, self.rbw, 10e3, 0)
        

    ## Recept the command, see if he has a question mark (so a GET command) else this is a SET command.
    ## Then switch on each case and return the answer.
    def readAndReturn(self,message):
        if("?" in message):
            # GET command
            if(message == "*IDN?"):
                # IDN used for the xml. A universal IDN is "Luxondes Simu,numero,version" but need to use the commands on the simulation.py from fast_simulation
                # Or you can create the xml then put the xml on CONFIG_SCPI folder of the folder Luxondes of your phone.
                return self.encode("SignalHound_SAx")
            if(message == "TRACE?"):
                # Get the trace then return it (ex: val1,val2,val3). On this case, a list of float without any comma but with a header containing the number of float
                return self.trace()
            if(message == "UNIT?"):
                # Return a string containing the unit.
                return self.encode(self.getUnit())
            if(message == "START?"):
                # Return a string containing the start.
                return self.encode(str(self.center-self.span/2))
            if(message == "STOP?"):
                # Return a string containing the stop.
                return self.encode(str(self.center+self.span/2))
            if(message == "CENTER?"):
                # Return a string containing the center.
                return self.encode(str(self.center))
            if(message == "SPAN?"):
                # Return a string containing the span.
                return self.encode(str(self.span))
            if(message == "ATT?"):
                # Return a string containing the attenuation (Do not affect Console or Scanphone).
                return self.encode(str(self.att))
            if(message == "RBW?"):
                # Return a string containing the RBW (Do not affect Console or Scanphone).
                return self.encode(str(self.rbw))
            if(message == "VBW?"):
                # Return a string containing the VBW (Do not affect Console or Scanphone).
                return self.encode(str(0))
        else:
            # SET command
            splits=message.split(" ")
            if(splits[0] == "CENTER"):
                # Set the center of the SA. Then Get it again on the case or the center is not applied.
                self.center=int(splits[1])
                sa_config_center_span(self.handle, self.center, self.span)
                return None
            # Because set span modify the rbw so the number of points on the array, we cannot modify the span.
##            if(splits[0] == "SPAN"):
##                # Set the span of the RSA.
##                self.setSpan(splits[1])
##                return None
        return None

    ## Add \n at the end of the message then transform it to a array of bytes.
    def encode(self,mes):
        return (mes+"\n").encode()

    ## Get the data from SA then convert it to a readable format for the client.
    ## Create a header begin with a # then the length of the number of value followed per the number of value.
    ## Ex: # + 4 + 1803
    def trace(self):
        values = sa_get_sweep_32f(self.handle)["max"]
        if(len(values)==self.sweep_length or self.oldText==None):
            lengthofLine=str(self.sweep_length*4)
            text=("#"+str(len(lengthofLine))+lengthofLine).encode()
            for i in values:
                text+=bytearray(struct.pack("f",i.view()))

            text+="\n".encode()
            self.oldText=text
        return self.oldText

        
## read all variables inside the file properties.txt.
def readPropertiesFile():
    bol=os.path.isfile('./properties.txt')
    if not bol:
        return [106.6e6,10e6]
    print("This server bridge will use the properties.txt")

    file1 = open('./properties.txt', 'r')
    lines = file1.readlines()

    # Default values
    values = [106.6e6,10e6]

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
    return values

## Launch the host server and link the CTRL+D (stop) and CTRL+Q (quit) with the stop of the server.
if __name__ == '__main__':
    values=readPropertiesFile()
    print("Center: "+str(values[0])+"Hz Span: "+str(values[1])+"Hz")

    hostserver=HostServer(values[0],values[1])

    signal.signal(signal.SIGTERM,hostserver.stop)
    signal.signal(signal.SIGINT,hostserver.stop)
    hostserver.init()
