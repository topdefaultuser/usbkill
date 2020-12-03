# -*- coding: UTF-8 -*-

"""
This file is a complete copy of usbkill.py. The file is used for hidden monitoring of usb devices.
(With hidden usb monitoring, the script console is not displayed). 
You can start hidden usb monitoring by running "usbkill.py" with the "--hiden" flag, after which "usbkill.py" will be launched, 
additional parameters will be checked and the "usbkill.pyw" script will be launched. or run "usbkill.pyw" immediately.
It is advisable to start hidden monitoring using "usbkill.py --hiden", because at startup, the startup parameters and other things will be checked, 
in case of any errors they will be displayed in the console, which will not work just by running "usbkill.pyw".
"""
from usbkill import * 



if __name__=="__main__":
	main()