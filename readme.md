# Description
<p>
Repositories which contains multiples bridges for different device where the bridge create a SCPI wrapper.
After the user can connect to the bridge with the Scanphone, Console or any device capable of read SCPI format.
https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments
</p>

## Bridge ETS Probe
#### Values returned
The bridge return a array of real containing [x,y,z,length] (no header)
#### Link
http://www.ets-lindgren.com/products/probes-monitors/electric-field-probes/9003/900307?page=Products-Item-Page
![bridges](/imgs/HI-6006.jpg)

## Bridge RSA Spectrum analyzer
#### Values returned
The bridge return a array of real of 32 bits with a header IEEE 754.
#### Link
https://www.tek.com/en/products/spectrum-analyzers/rsa306
https://www.tek.com/en/products/spectrum-analyzers/rsa500

![bridges](/imgs/Tek-rsa306b_03a_h.png)
![bridges](/imgs/Tek-rsa507a_04a-504px.png)
#### Compatibility
Tested with RSA300 and RSA500</br>
Compatible with all RSA300,600,500 devices.

#### Known issues
- Connection can be blocked per Window. Need to restart the bridge.
- The RSA reset its center/span when you disconnect from them, causing a "incompatibility" to use SignalVu before for setup.
Meaning you can't pre-set the center/span with SignalVu before doing your measurement with the EM-Scanphone. (That's why we're using a properties file)
- No working on Linux/MacOS.


## Bridge SA44B Spectrum analyzer
#### Values returned
The bridge return a array of real of 32 bits with a header IEEE 754.
#### Link
https://signalhound.com/products/usb-sa44b/
![bridges](/imgs/SA44B-single.jpg)
#### Compatibility
Tested with SA44B Spectrum analyzer</br>
Compatible with all RSA300,600,500 devices.

#### Known issues
- No working on Linux/MacOS.

## Simulation
#### Values returned
- If probe: return a array of real containing [x,y,z,length] (no header)
- If spectrum analyzer: return a array of 1024 real of 32 bits with a header IEEE 754.
