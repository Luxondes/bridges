import math


class Sphere():

    def  __init__(self):
        coupeX=360
        coupeY=180
        latitudes=64
        longitudes=120

        self.latitude_increment = coupeX / latitudes
        self.longitude_increment = coupeY / longitudes
        self.latitude_pas = latitudes / coupeX
        self.longitude_pas = longitudes / coupeY
        self.latitudesFinal = latitudes+1
        self.longitudesFinal = longitudes+2;
        self.nbLines = latitudesFinal * longitudesFinal

##        self.nbLines=11520
        self.nbFreq=30

        data,freqs=self.createFakeData()

        self.freqs=freqs

        self.values=data


    def createFakeData(self):
        fakeData=[]
        minv=-6
        maxv=6
        
        step=(maxv-minv)/self.nbLines
        for i in range(self.nbLines):
            subList=[]
            for j in range(self.nbFreq):
                subList+=[minv+step*random.randrange(0,i+1)]            
            fakeData+=[subList]

        frequencies=[]
        for j in range(self.nbFreq):
            frequencies+=[10+0.1*j]      
        return (fakeData,frequencies)


    def setValue(x,y,z,listOfValue):
    polarX,polarY = self.coordPosToPolar(x,y,z, valueScale);

    indice = self.getPolarToIndice(polarX,polarY);

    self.values[indice]=listOfValue

    


    
    
    
    def coordPosToPolar(self, coordX,coordY,coordZ, rayon):
            return math.degrees(math.atan2(coordY, coordX)), //Latitude Degree
                math.degrees(math.acos(coord.z / rayon));  // Longitude Degree
    # Retourne l'indice dans le tableau de valeurs
    def getPolarToIndice(self,polarX,polarY):
            return (int)(polarY* self.longitude_pas) * (self.latitudesFinal) + (int)(polarX * self.latitude_pas);

    def getFreqs(self):
        freqsString=""
        for val in self.freqs:
            freqsString+=str(val)+"\t"
        return freqsString
    def writeData(self,file):
        for sublist in data:
            toWrite=""
            for val in sublist:
                toWrite+=str(val)+"\t"
            for i in range(0,len(self.freqs)-len(self.sublist)):
                toWrite+="0\t"
            file.write(toWrite[:-2]+"\n")
