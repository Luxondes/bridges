# Installation

## Incompatibility
<p>
It is impossible to have 2 connections at the same time with the RSA. SignalVU SW cannot be opened at the same time as the RSA bridge.
</p>
 

## RSA
<p>
Download and install the library RSA : https://www.tek.com/en/products/spectrum-analyzers/rsa306</br>
On their website, click on Download then Software and download the RSA Application Programming Interface (API) of your computer.
</p>

## Python
<p>
Download and install python 3+ : https://www.python.org/downloads/</br>
Be sure to have checked "Add Python environment variables" on the Python installation. Else relaunch the Python program.
</p>

# Launch
<p>
To launch the script, double click on start_rsa.

If the shell do not print any "Waiting connection" after 5 seconds, ctrl+C can unlock the issue.

To stop the script, you will need to ctrl+C and wait few seconds or just close the shell.
</p>
# Variables

Modify values of properties.ini for setup RSA.

Start/stop can be used but will override center/span.
