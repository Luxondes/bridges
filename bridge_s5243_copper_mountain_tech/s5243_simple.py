
from zipfile import ZipFile
import pyvisa
import time
import switch_loop
import os
import export_xml
import datetime



# We can't use the sleep function because it rely on the OS clock which is not precise enough in Windows environments (approx. 16ms)
# Instead we create a Delay_ms function which use time.perf_counter() which use the most precise clock available on the system (less than 1ms)
def delay_ms(ms):
    t1 = time.perf_counter()
    t2 = t1
    while (((t2-t1)*10**3) < ms):
        t2 = time.perf_counter()
    print("Elapsed time: ", ((t2-t1)*10**3), " ms")
    return ((t2-t1)*10**3)

def createName():
    currentTime = datetime.datetime.now()
    year=str(currentTime.year)
    month=str(currentTime.month)
    if(len(month)==1):
        month="0"+month
    day=str(currentTime.day)
    if(len(day)==1):
        day="0"+day
    hour=str(currentTime.hour)
    if(len(hour)==1):
        hour="0"+hour
    minute=str(currentTime.minute)
    if(len(minute)==1):
        minute="0"+minute
    second=str(currentTime.second)
    if(len(second)==1):
        second="0"+second
    return year+month+day+"-"+hour+minute+second

def createDat(path,values):
    file = open(path, "w")
    for sublist in values:
        file.write(sublist)
    file.close()

def createSphere(freqs,values):
    startCom=export_xml.StartComponent()
    comCom=export_xml.ComponentComponent()
    setupCom=export_xml.SetupComponent()
    probeCom=export_xml.ProbeComponent()
    datasphericalCom=export_xml.DataSphericalComponent()

    datasphericalCom.r0_coordinates="300mm"
    datasphericalCom.a0_coordinates="0mm"
    datasphericalCom.b0_coordinates="160mm"
    datasphericalCom.rmax_coordinates="300mm"
    datasphericalCom.amax_coordinates="360mm"
    datasphericalCom.bmax_coordinates="20mm"
    datasphericalCom.rstep_coordinates="0mm"
    datasphericalCom.astep_coordinates="20mm"
    datasphericalCom.bstep_coordinates="-26.667mm"
    datasphericalCom.unit="GHz"
    name=createName()

    datasphericalCom.dat_Filename=name+".dat"

    file_paths = ["./"+name+".xml","./"+name+".dat"]

    datasphericalCom.listF=freqs
    createDat(file_paths[1],values)


    export_xml.create_xml_standard(file_paths[0],startCom,comCom,setupCom,probeCom,datasphericalCom)
    
  
  
    # printing the list of all files to be zipped
    print('Following files will be zipped:')
    for file_name in file_paths:
        print(file_name)
  
    # writing files to a zipfile
    with ZipFile(name+'.lxd','w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)
            os.remove(file)
def convertDataVNAToDataLuxondes(stringresult,isFreq=True):
        a = stringresult.split(",")
        b = [float(m) for m in a]
        if(not isFreq):
            b=b[::2]
        else:
            b=[m/1000000000 for m in b]
        c=""
        for val in b:
            c+=str(val)+"\t"
        if (not isFreq):
            c=c[:-1]+"\n"
        return c
    
        
class Main():
    def  __init__(self):
        rm = pyvisa.ResourceManager('@py') # use pyvisa-py as backend, must install pyvisa-py 

        #Connect to a Socket on the local machine at 5025
        try:
            self.CMT = rm.open_resource('TCPIP0::127.0.0.1::9001::SOCKET')
        except:
            print("Failure to connect to VNA!")
            print("Check network settings")
            return
        #The VNA ends each line with this. Reads will time out without this
        self.CMT.read_termination='\n'
        #Set longer timeout period for slower sweeps
        self.CMT.timeout = 10000
        ''' set up the VNA '''
        self.CMT.write('DISP:WIND:SPL 1') # allocate 2 trace windows 
        self.CMT.write('CALC1:PAR:COUN 1') # 2 Traces
        self.CMT.write('CALC1:PAR1:DEF S11') #Choose S21 for trace 1
        self.CMT.write('CALC1:PAR1:SEL')
        self.CMT.write('CALC1:FORM MLOG')
        self.CMT.write('TRIG:SOUR BUS')
        self.CMT.write("SENS:FREQ:SPAN 1000000000") 
        self.CMT.write("SENS:FREQ:CENTER 5500000000") 


        # Always end an *OPC? command after all the VNA setups to make sure the setups are 
        # complete before making measurement
        self.CMT.query('*OPC?')

        self.switch=switch_loop.Switch()


        

        # Do a sweep from port 1 to 16 with the common port 1 and a delay of 10 ms between each switch
        self.sweep_port( 1)
    
    def sweep_port(self, common_port):
        if (type(common_port) != int):
            return ("common_port value must be an integer.")


        values=[]

        # Read frequency data (NOTE: the data read from VNA is a string that contains comma separated data points)
        # Trigger a measurement
        self.CMT.write('TRIG:SING') #Trigger a single sweep
        self.CMT.query('*OPC?') #Wait for measurement to complete
        self.CMT.write('CALC1:PAR1:SEL')
        Freq = self.CMT.query("SENS1:FREQ:DATA?") #Get data as string
        Freq = convertDataVNAToDataLuxondes(Freq)



        

        listvalues=[[],[],[],[],[],[],[],[],[],[]]
        
        time_interval = 10 # in milliseconds
        if (time_interval < 0.4):
            return ("Baudrate limit exeeded, increase the time interval.")
        
        for i in range(1,11):
            data_to_send = self.switch.select_port(common_port, i)
            self.switch.correlator.write(data_to_send.encode('ascii'))
            print("Command sent: ", data_to_send)

            '''start VNA measurement, put this section inside a loop to measure continuously '''
            # Trigger a measurement
            self.CMT.write('TRIG:SING') #Trigger a single sweep
            self.CMT.query('*OPC?') #Wait for measurement to complete
            # Read log mag data
            
            M = self.CMT.query("CALC1:DATA:FDAT?") #Get data as string
            M = convertDataVNAToDataLuxondes(M,False)
            listvalues[i-1]+=[M]

            delay_ms(time_interval)
        self.switch.close()


        values=[]
        for i in range(9,-1,-1):
            for j in range(18):
                values+=[listvalues[i][0]]

        createSphere(Freq,values)





if __name__ == "__main__":
    Main()



