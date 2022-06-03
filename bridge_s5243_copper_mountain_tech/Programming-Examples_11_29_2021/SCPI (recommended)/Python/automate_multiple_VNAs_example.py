# -*- coding: utf-8 -*-
"""
Created on Wed Jul 28 15:54:24 2021

@author: Patrick.l
"""

import subprocess



# note the space in front of /SocketServer:on. It must have this space.
subprocess.run(['C:/VNA/S2VNA_copy1/S2VNA.exe', ' /SocketServer:on /SocketPort:5026 /SerialNumber:12345678 /visible:on'])