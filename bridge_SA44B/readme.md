# Installation

## SA44B
<p>
Look if the file sa_api.dll is present on bridge_SA44B/sources/sadevice/ otherwise follow these directives:
Download and install the library SA44B :
https://signalhound.com/software/signal-hound-software-development-kit-sdk/
</br>
On their website, click on "Download the Signal Hound Software Development Kit" then decompress the zip and copy paste signal_hound_sdk/device_apis/sa_series/win/lib/x64 on bridge_SA44B/sources/sadevice.
</p>

## Python
<p>
Download and install python 3+ : https://www.python.org/downloads/</br>
Be sure to have checked "Add Python environment variables" on the Python installation. Else relaunch the Python program.
</p>

## VS2012
<p>
Download and install VS2012 C++ re-distributables for API development</br>
</p>

# Launch
<p>
To launch the script, double click on start_bridge_sa44b.

If the shell do not print any "Waiting connection" after 5 seconds, ctrl+C can unlock the issue.

To stop the script, you will need to ctrl+C and wait few seconds or just close the shell.
</p>

# Variables

Modify values of properties.ini for setup SA44B.
