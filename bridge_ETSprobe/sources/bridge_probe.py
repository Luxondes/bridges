#!/usr/bin/env python
import socket
import signal
import struct
import time
import os
from ctypes import *
class HostServer():
    def  __init__(self):
        self.dataSaved=[]
        self.isRunning=False
        self.thread=None
        self.handle=c_long (0)
        self.status =None
        self.messageToSend=None
        self.connected=False
        self.connection=None
        self.client_address=None
        self.server_address=None
        self.hostsocket=None

        self.info="Err"
        self.unit="Err"

        self.xyzField=c_float(0)
        self.xField=c_float(0)
        self.yField=c_float(0)
        self.zField=c_float(0)

    def stop(self,signum,frame):
        self.isRunning=False
        self.etsProbeDll.ETS_RemoveProbe.argtypes=[c_long]
        self.etsProbeDll.ETS_RemoveProbe.restype=c_int
        self.status =self.etsProbeDll.ETS_RemoveProbe (self.handle)
    def __run(self):
        timeoutcustom=0
        self.isRunning=True
        try:
            self.create_server_socket()
            if not self.isRunning:
                self.hostsocket.close()
                return
            while(self.isRunning):
                self.accept_new_connection()
                timeoutcustom=0
                if self.connected:
                    try:
                        while(self.connected):
                            if not self.isRunning:
                                self.close_socket()
                                break
                            try:
                                data=self.connection.recv(4096).decode()
                                if(data==""):
                                    print('end connection')
                                    self.close_socket()
                                    pass
                                if (data):
                                    self.read_data(data)

                            except socket.timeout:
                                timeoutcustom+=1
                                if timeoutcustom > 5:
                                    self.close_socket()

                            except socket.error:
                                self.close_socket()
                                pass
                    finally:
                        print("end while connected")
                        self.close_socket()
        finally:
            print("end while running")
            self.hostsocket.close()
            self.hostsocket=None
            self.isRunning=False

    def create_server_socket(self):
        self.server_address=("0.0.0.0",9001)
        self.hostsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.hostsocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

        try:
            self.hostsocket.bind(self.server_address)
        except:
            self.isRunning=False

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

    def accept_new_connection(self):
        try:
            self.connection, self.client_address = self.hostsocket.accept()
            self.connection.settimeout(10)
            print("Accepting new connection")
            self.connected=True
        except socket.timeout:
            return

    def read_data(self,data):
        self.dataSaved+=[data]
        if('\n' in data):
            message=""
            for dat in self.dataSaved:
                message=message + dat
            self.dataSaved=[]
            splits=message.split("\n")
            for i in range(0,len(splits)-1):
                answer=self.readAndReturn(splits[i].strip().upper())
                if(answer != None):
                    self.connection.send(answer)

    def close_socket(self):
        if self.connection!=None :
            self.connection.close()
            self.dataSaved=[]
        self.connected=False
    def init(self):
        server_name=socket.gethostname()
        print(server_name)

        # Load DLL into memory.
        os.chdir(".")
        self.etsProbeDll =None
##        try:
        self.etsProbeDll = WinDLL (".\sources\ETSProbe.dll")
##        except:
##            self.etsProbeDll = WinDLL ("ETSProbe.dll")
            
        self.etsProbeDll.ETS_CreateProbe.argtypes=c_char_p,POINTER(c_long),c_char_p,c_char_p
        self.etsProbeDll.ETS_CreateProbe.restype=c_int

        p4 = b'HI-Any'
        switchedToFP=False

        test_i=0
        while(True):
            p1 = ("Probe #"+str(test_i)).encode()
            p3 = ("Com"+str(test_i)).encode()
            self.status =self.etsProbeDll.ETS_CreateProbe (p1, byref(self.handle),p3, p4)
            if(self.status==0):
                break
            if(self.status==3):
                test_i+=1
                if(test_i==10):
                    if(switchedToFP):
                        print("Error, found any probe of Com[0-10] of family HI or FP")
                        return False
                    test_i=0
                    p4 = b'FP-Any'
                    switchedToFP=True
                continue


        self.etsProbeDll.ETS_ReadFieldSynchronous.argtypes=c_int,POINTER(c_float),POINTER(c_float),POINTER(c_float),POINTER(c_float)
        self.etsProbeDll.ETS_ReadFieldSynchronous.restype=c_int


        self.etsProbeDll.ETS_GetUnitsString.argtypes=c_int,c_char_p,c_int
        self.etsProbeDll.ETS_GetUnitsString.restype=c_int

        self.etsProbeDll.ETS_Model.argtypes=c_int,c_char_p,c_int
        self.etsProbeDll.ETS_Model.restype=c_int

        self.etsProbeDll.ETS_ProbeName.argtypes=c_int,c_char_p,c_int
        self.etsProbeDll.ETS_ProbeName.restype=c_int

        length_buffer_array=120

        p1=create_string_buffer(length_buffer_array)

        self.status =self.etsProbeDll.ETS_GetUnitsString (self.handle,p1, length_buffer_array)
        self.unit=p1.value.decode()

        self.status =self.etsProbeDll.ETS_ProbeName (self.handle,p1, length_buffer_array)
        self.info=p1.value.decode()

        self.status =self.etsProbeDll.ETS_Model (self.handle,p1, length_buffer_array)
        self.info+=" "+p1.value.decode()

        self.__run()
        return True

    def isRunning(self):
        return self.isRunning
    def readAndReturn(self,message):
        if(message == "*IDN?"):
            return self.encode(self.info)
        if(message == ":TRAC? TRACE1"):
            return self.trace()
        if(message == ":UNIT:POWER?"):
            return self.encode(self.unit)
        return None

    def encode(self,mes):
        return (mes+"\n").encode()
    def trace(self):
        self.status =self.etsProbeDll.ETS_ReadFieldSynchronous(self.handle,byref(self.xField),byref(self.yField),byref(self.zField),byref(self.xyzField))
        values=(self.xField.value,self.yField.value,self.zField.value,self.xyzField.value)
        text="".encode()
        for i in values:
            text+=bytearray(struct.pack("f",i))
        text+="\n".encode()
        return text

## Launch the host server and link the CTRL+D (stop) and CTRL+Q (quit) with the stop of the server.
if __name__ == '__main__':
    hostserver=HostServer()

    signal.signal(signal.SIGTERM,hostserver.stop)
    signal.signal(signal.SIGINT,hostserver.stop)
    hostserver.init()
