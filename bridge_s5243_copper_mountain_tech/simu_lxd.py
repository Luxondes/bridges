from zipfile import ZipFile
import os
import export_xml
import datetime
import random
import sphere

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

def createDat(path,sphere):
    file = open(path, "w")
    sphere.writeData(file)
    file.close()


 
def main():
    # path to folder which needs to be zipped
##    directory = './exportDir'
##    if(os.path.isdir(directory)):
##        None
##        # Exist
##    else:
##        os.mkdir(directory)


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
    datasphericalCom.astep_coordinates="0.5mm"
    datasphericalCom.bstep_coordinates="-9.33mm"
    datasphericalCom.unit="MHz"
    
    

    name=createName()

    datasphericalCom.dat_Filename=name+".dat"

    file_paths = ["./"+name+".xml","./"+name+".dat"]

    sphere=sphere.Sphere()

    
    datasphericalCom.listF=sphere.getFreqs()
    
    createDat(file_paths[1],sphere.values)
    
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
        
    
  
    print('All files zipped successfully!')        
  
  
if __name__ == "__main__":
    main()
