![usbkill](Resources/USBKillBanner.gif)

« usbkill » is an anti-forensic kill-switch that waits for a change on your USB ports and then immediately shuts down your computer.

To run:

```shell
sudo python usbkill.py
```
or
```shell
sudo python3 usbkill.py
```

Related project; same idea, but implemented as a Linux driver: https://github.com/NateBrune/silk-guardian


### Why?

Some reasons to use this tool:

- In case the police or other thugs come busting in (or steal your laptop from you when you are at a public library, as happened to Ross). The police commonly uses a « [mouse jiggler](http://www.amazon.com/Cru-dataport-Jiggler-Automatic-keyboard-Activity/dp/B00MTZY7Y4/ref=pd_bxgy_pc_text_y/190-3944818-7671348) » to keep the screensaver and sleep mode from activating.
- You don’t want someone to add or copy documents to or from your computer via USB.
- You want to improve the security of your (encrypted) home or corporate server (e.g. Your Raspberry).

> **[!] Important**: Make sure to use disk encryption for all folders that contain information you want to be private. Otherwise they will get it anyway. Full disk encryption is the easiest and surest option if available

> **Tip**: Additionally, you may use a cord to attach a USB key to your wrist. Then insert the key into your computer and start usbkill. If they steal your computer, the USB will be removed and the computer shuts down immediately.

### Feature List
(version 1.0-rc.5)
- Works on windows.
- Added hidden work mode.
- Added commands to add and remove allowed usb devices.  Use ```usbkill.py --append``` to add device to whitelist.
Use ```usbkill.py --remove``` to remove usb device from whitelist.
- Storing serial numbers of usb devices in a hashed form

### Feature List
(version 1.0-rc.4)
- Compatible with Linux, *BSD and OS X.
- Shutdown the computer when there is USB activity.
- Customizable. Define which commands should be executed just before shut down.
- Ability to whitelist a USB device.
- Ability to change the check interval (default: 250ms).
- Ability to melt the program on shut down.
- RAM and swap wiping.
- Works with sleep mode (OS X).
- No dependency except secure-delete iff you want usbkill to delete files/folders for you or if you want to wipe RAM or swap. ```sudo apt-get install secure-delete```
- Sensible defaults


### Supported command line arguments (partially for devs):

- --help: show help message, exit.
- --version: show version of the program, exit.
- --append: To add a usb device to the whitelist, you need to run the program with the '--append' flag, then insert a new usb device and wait 3-4 seconds. To add multiple usb devices, you need to repeat this procedure for each device separately.
- --remove: To remove a usb device from whitelist, you need to run the program with the '--remove' flag, then insert the usb device and wait 3-4 seconds. Each device is removed individually. 
- --hiden:            Start program in hiden mode (without console).
- --no-shut-down: if a malicious change on the USB ports is detected, execute all the (destructive) commands you defined in settings.ini, but don’t turn off the computer.

