#!/usr/bin/env python
import socket
import signal
import struct
import time
import sys

## Host server which simulate a spectrum analyser or probe for any client.
class HostServer():
    def  __init__(self,typesimu):
        self.dataSaved=[]
        self.isRunning=False
        self.thread=None
        self.messageToSend=None
        self.connected=False
        self.connection=None
        self.client_address=None
        self.server_address=None
        self.hostsocket=None
        self.linesDat=None
        self.typesimu=typesimu

    ## Stop the host server
    def stop(self,signum,frame):
        self.isRunning=False

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
##                                print(data)
                                if(data==""):
                                    print('end connection')
                                    self.close_socket()
                                    #closed
                                    pass
                                # Get Command, compute the command.
                                if (data):
                                    self.read_data(data)

                            except socket.timeout as e:
                                print(e)
                                # If too many exception, close the client.
                                timeoutcustom+=1
                                if timeoutcustom > 5:
                                    self.close_socket()

                            except socket.error as e:
                                print(e)
                                self.close_socket()
                                pass
                    except Exception as e:
                        print(e)
                    finally:
                        print("end while connected")
                        self.close_socket()
        finally:
            print("end while running")
            self.hostsocket.close()
            self.hostsocket=None
            self.isRunning=False


    ## Create the server socket on the PC (This code work on Linux or Windows. Untested for Mac)
    ## The socket will be on the ip of the PC and the port choosen.
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
        print("Simulation port: "+str(port))
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
        self.connected=False

    ## Recover all lines of the .dat of the simulation choosen. Then run the server.
    def init(self):
        server_name=socket.gethostname()
        print(server_name)
        if(self.typesimu==0):
            file1=open(".\sources\Simulation_test.dat","r")
        else:
            file1=open(".\sources\Simulation_probe.dat","r")
        lines=file1.readlines()
        self.linesDat=[]
        for line in lines:
            self.linesDat+=[self.fromLine(line.strip())]
        file1.close()

        self.__run()

    def isRunning(self):
        return self.isRunning

    ## Recept the command, these simulations do not have any setter only getter.
    ## Then switch on each case and return the answer.
    def readAndReturn(self,message):
        if(self.typesimu == 1):
            return self.read_probe(message)
        return self.read_frequency(message)

    ## readAndReturn for Probe
    def read_probe(self,message):
        if(message == "*IDN?"):
            return self.encode("Probe_Simulation")
        if(message == ":TRAC? TRACE1"):
            idx=int((time.time()%10)/10*len(self.linesDat))
            return self.ofLine_probe(idx)
        if(message == ":UNIT:POWER?"):
            return self.encode("U/m")
        return None

    ## readAndReturn for Frequency.
    def read_frequency(self,message):
        if(message == "*IDN?"):
            return self.encode("Luxondes Simu,numero,version")
        if(message == ":FREQ:STAR?"):
            return self.encode("100000")
        if(message == ":FREQ:STOP?"):
            return self.encode("110000")
        if(message == ":FREQ:CENTER?"):
            return self.encode("10500")
        if(message == ":FREQ:SPAN?"):
            return self.encode("500")
        if(message == ":TRAC? TRACE1"):
            idx=int((time.time()%10)/10*len(self.linesDat))
            return self.ofLine(idx)
        if(message == ":UNIT:POWER?"):
            return self.encode("DBM")
        if(message == ":SWE:TIME?"):
            return self.encode("1")
        if(message == "INP:ATT?"):
            return self.encode("10")
        if(message == ":DISP:TRAC:Y:SCAL?"):
            return self.encode("100")
        if(message == ":DISP:TRAC:Y:RLEV?"):
            return self.encode("0")
        if(message == "BAND?"):
            return self.encode("10000")
        if(message == "BAND:VID?"):
            return self.encode("10000")
        if(message == "CALC:MARK:X?"):
            return self.encode("105000")
        if(message == "CALC:MARK:Y?"):
            idx=int((time.time()%10)/10*len(self.linesDat))
            
            l=self.linesDat[idx]
            angle=(idx*2*360/len(self.linesDat))%360
            return self.encode(str(l[int(len(l)/2)])+" , "+str(angle))        
        return None

    ## Add \n at the end of the message then transform it to a array of bytes.
    def encode(self,mes):
        return (mes+"\n").encode()

    ## Transform the array of float to a array of byte with a header
    ## The header begin with a # then the length of the number of value followed per the number of value.
    ## Ex: # + 4 + 1803
    def ofLine(self,idx):
        l=self.linesDat[idx]
        lengthofLine=str(len(l)*4)
        text=("#"+str(len(lengthofLine))+lengthofLine).encode()
        for i in l:
            text+=bytearray(struct.pack("f",i))
        text+="\n".encode()
        return text

    ## Transform the array of float to a array of byte containing a array of float. No header because fixed to 4 values.
    def ofLine_probe(self,idx):
        l=self.linesDat[idx]
        text="".encode()
        for i in l:
            text+=bytearray(struct.pack("f",i))
        text+="\n".encode()
        return text

    ## Transform the line of the .dat to a array of float.
    def fromLine(self,line):
        sp=line.split('\t')
        dbs=[0]*len(sp)
        try:
            for i in range(0,len(sp)):
                dbs[i]=float(sp[i])
        except:
            None
        return dbs

## Launch the host server and link the CTRL+D (stop) and CTRL+Q (quit) with the stop of the server.
## Simu 0 is frequency of 1803 values, Simu 1 is a probe for vector field test
if __name__ == '__main__':
    typesimu=0
    if(len(sys.argv) > 1 ):
        if(sys.argv[1].startswith("p")):
            typesimu=1

    hostserver=HostServer(typesimu)

    signal.signal(signal.SIGTERM,hostserver.stop)
    signal.signal(signal.SIGINT,hostserver.stop)
    hostserver.init()
