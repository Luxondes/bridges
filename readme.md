# Description
***
<p>
Repositories which contains multiples bridges for different device where the bridge create a SCPI wrapper.
After the user can connect to the bridge with the Scanphone, Console or any device capable of read SCPI format.
https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments
</p>

## Bridge ETS Probe
***
#### Values returned
The bridge return a array of real containing [x,y,z,length] (no header)
#### Link
http://www.ets-lindgren.com/products/probes-monitors/electric-field-probes/9003/900307?page=Products-Item-Page

## Bridge RSA Spectrum analyzer
***
#### Values returned
The bridge return a array of real of 32 bits with a header IEEE 754.
#### Link
https://www.tek.com/en/spectrum-analyzer/rsa306-manual-10
#### Compatibility
Tested with RSA300 and RSA500
#### Issues
- Connection can be blocked per Window. Need to restart the bridge.
- Their RSA reset their center/span when you disconnect from them, causing a "incompatibility" to use SignalVu before for setup.

## Simulation
***
#### Values returned
- If probe: return a array of real containing [x,y,z,length] (no header)
- If spectrum analyzer: return a array of 1024 real of 32 bits with a header IEEE 754.
