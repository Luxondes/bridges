##import xml.etree.ElementTree as ET
from xml.dom import minidom
import os 
class SetupComponent():
    isTime=False
    rbw_Config=None
    vbw_Config=None
    swp_Config=None
    ref_lev_Config=None
    descSetup_Config=None
    att_Config=None
    unitFrequence_Transducer=None
    valueFrequences_Transducer = []
    def  __init__(self):
        None
class ProbeComponent():
    isTime=False
    name=None
    field=None
    notes=None
    unit=None
    values=[]
    valuesPerf=[]
    def  __init__(self):
        None        
class DataSphericalComponent():
    r0_coordinates=None
    a0_coordinates="0mm"
    b0_coordinates="359mm"
    rmax_coordinates=None
    amax_coordinates="180mm"
    bmax_coordinates="180mm"
    rstep_coordinates=None
    astep_coordinates=None
    bstep_coordinates=None
    coordinates="none"
    isTime=False
    name=None
    unit=None
    listF=None
    unit_Measurement="dB(V/m)"
    x_Measurement="mm"
    y_Measurement="mm"
    z_Measurement="mm"
    dat_Filename=None
    dat_format=None
    transparentValue=None
    def  __init__(self):
        None 
class ComponentComponent():
    componentName=None
    componentNote=None
    swp_Config=None
    xoffset_Image="0"
    yoffset_Image="0"
    zoffset_Image=None
    xsize_Image=None
    ysize_Image=None
    zsize_Image=None
    path_Image=None
    unit_Image=None
    def  __init__(self):
        None
class StartComponent():
    nameData=None
    date=None
    disclaimer=None
    versionScanphone=None
    def  __init__(self):
        None        
        
def create_xml_standard(pathname,start,component,setup,probe,dataspherical):
    document = minidom.Document()
      
    root = document.createElement('EmissionScan') 
    document.appendChild(root)
      
    addStart(document,root,start)
    addComponent(document,root, component);
    addSetup(document,root, setup);
    addProbe(document,root,probe);
    addDataSpherical(document,root, dataspherical);
##    addSpecialType(document,root,specialType);
      
    xml_str = document.toprettyxml(indent ="\t") 
      
    with open(pathname, "w") as f:
        f.write(xml_str)

def addStart(document,root, startComponent):
    tag(document,root, "Nfs_ver", "1.0");
    tag(document,root,  "Filename", startComponent.nameData);
    tag(document,root,   "File_ver", "1.0");
    tag(document,root,   "Date", startComponent.date);
    tag(document,root,   "Source");
    tag(document,root,   "Notes", startComponent.versionScanphone);
    tag(document,root,  "Disclaimer", startComponent.disclaimer);
    tag(document,root,   "Copyright", "LUXONDES");

def addComponent(document,root, componentComponent):
    leafComponent =tag(document,root, "Component");
    
    tag(document,leafComponent, "Name", componentComponent.componentName);
    tag(document,leafComponent, "Manufacturer");
    tag(document,leafComponent, "Notes", componentComponent.componentNote);
    
    leafImage = tag(document,leafComponent, "Image")
    
    if (componentComponent.path_Image != None) :
        tag(document,leafImage, "Path", componentComponent.path_Image);
    else:
        tag(document,leafImage, "Path");

    tag(document,leafImage, "Unit", componentComponent.unit_Image);
    tag(document,leafImage, "Xsize", componentComponent.xsize_Image);

    if (componentComponent.zsize_Image != None) :
        tag(document,leafImage, "Zsize", componentComponent.zsize_Image);
    else :
        tag(document,leafImage, "Ysize", componentComponent.ysize_Image);
    
    tag(document,leafImage, "Xoffset", componentComponent.xoffset_Image);
    tag(document,leafImage, "Yoffset", componentComponent.yoffset_Image);
    if (componentComponent.zoffset_Image != None) :
        tag(document,leafImage, "Zoffset", componentComponent.zoffset_Image);
def addSetup(document,root,setupComponent):
    leafSetup =tag(document,root, "Setup");
    tag(document,leafSetup, "Notes");
    leafConfig =tag(document,leafSetup, "Setup");
    tag(document,leafConfig, "Notes", setupComponent.descSetup_Config);
    tag(document,leafConfig, "Att", setupComponent.att_Config);
    tag(document,leafConfig, "Average");
    tag(document,leafConfig, "Ref_Level", setupComponent.ref_lev_Config);
    tag(document,leafConfig, "Rbw", setupComponent.rbw_Config);
    tag(document,leafConfig, "Vbw", setupComponent.vbw_Config);
    tag(document,leafConfig, "Swp", setupComponent.swp_Config);
    leafTransducer =tag(document,leafSetup, "Transducer");
    tag(document,leafTransducer, "Notes");
    if (setupComponent.unitFrequence_Transducer != None):
        if(setupComponent.isTime):
            nameTag="Times"
        else:
            nameTag="Frequencies"
        leafList=tag(document,leafTransducer, nameTag);
        
        tag(document,leafList, "Unit", setupComponent.unitFrequence_Transducer)
        longString=""
        for val in  setupComponent.valueFrequences_Transducer:
            longString+=val + " ";
        tag(document,leafList, "List", longString);
    tag(document,leafTransducer, "Gain");


def addProbe(document,root, probeComponent):
    if(probeComponent==None):
        return
    leafProbe =tag(document,root, "Probe")

    tag(document,leafProbe, "Name", probeComponent.name)
    tag(document,leafProbe, "Field", probeComponent.field)
    tag(document,leafProbe, "Notes", probeComponent.notes)
    if(probeComponent.isTime):
        nameTag="Times"
    else:
        nameTag="Frequencies"
    leafList=tag(document,leafProbe, nameTag);
    tag(document,leafList, "Unit", probeComponent.unit);
    longString=""
    for val in  probeComponent.values:
        longString+=val + " ";
    tag(document,leafList, "List", longString);
    
    leafList=tag(document,leafProbe, "Perf_factor");
    tag(document,leafList, "Unit");
    longString=""
    for val in   probeComponent.valuesPerf:
        longString+=val + " ";
    tag(document,leafList, "List", longString);    
    
    

def addDataSpherical(document,root, dataSphericalComponent):
    leafData =tag(document,root, "Data")
    
    tag(document,leafData, "Notes");
    tag(document,leafData, "Coordinates", dataSphericalComponent.coordinates);
    tag(document,leafData, "R0", dataSphericalComponent.r0_coordinates);
    tag(document,leafData, "A0", dataSphericalComponent.a0_coordinates);
    tag(document,leafData, "B0", dataSphericalComponent.b0_coordinates);
    tag(document,leafData, "Rmax", dataSphericalComponent.rmax_coordinates);
    tag(document,leafData, "Amax", dataSphericalComponent.amax_coordinates);
    tag(document,leafData, "Bmax", dataSphericalComponent.bmax_coordinates);
    tag(document,leafData, "Rstep", dataSphericalComponent.rstep_coordinates);
    tag(document,leafData, "Astep", dataSphericalComponent.astep_coordinates);
    tag(document,leafData, "Bstep", dataSphericalComponent.bstep_coordinates);


    if (dataSphericalComponent.unit != None) :
        if(dataSphericalComponent.isTime):
            nameTag="Times"
        else:
            nameTag="Frequencies"
        leafList=tag(document,leafData, nameTag);
        tag(document,leafList, "Unit", dataSphericalComponent.unit);
        tag(document,leafList, "List", dataSphericalComponent.listF);            

    leafMeasure =tag(document,leafData, "Measurement")
    tag(document,leafMeasure, "Unit", dataSphericalComponent.unit_Measurement);
    tag(document,leafMeasure, "Unit_x", dataSphericalComponent.x_Measurement);
    tag(document,leafMeasure, "Unit_y", dataSphericalComponent.y_Measurement);
    tag(document,leafMeasure, "Unit_z", dataSphericalComponent.z_Measurement);
    tag(document,leafMeasure, "Data_files", dataSphericalComponent.dat_Filename);

    
def tag(document,leaf,nameTag,contentTag=None):
    child = document.createElement(nameTag)
    leaf.appendChild(child)
    if(contentTag != None):
        text = document.createTextNode(str(contentTag))
        child.appendChild(text)
    return child
