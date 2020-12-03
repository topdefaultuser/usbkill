#!/usr/bin/env python

#             _     _     _ _ _ 
#            | |   | |   (_) | |
#  _   _  ___| |__ | |  _ _| | |
# | | | |/___)  _ \| |_/ ) | | |
# | |_| |___ | |_) )  _ (| | | |
# |____/(___/|____/|_| \_)_|\_)_)
#
#
# Hephaestos <hephaestos@riseup.net> - 8764 EF6F D5C1 7838 8D10 E061 CF84 9CE5 42D0 B12B
# <https://github.com/hephaest0s/usbkill>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


"""
The files usbkill.py and usbkill.pyw are the same file. 
Usbkill.pyw is for running the script in stealth mode (without showing the console) 
while usbkill.py is used when running the script with the console showing.
"""

__version__ = "1.0-rc.5"

import re
import subprocess
import platform
import ctypes
import os
import sys
import time

import utils

# Get the current platform
CURRENT_PLATFORM = platform.system().upper()

# Darwin specific library
if CURRENT_PLATFORM.startswith("DARWIN"):
	import plistlib

if CURRENT_PLATFORM.startswith("WINDOWS"):
	import winreg

# We compile this function beforehand for efficiency.
DEVICE_RE = [re.compile(".+ID\s(?P<id>\w+:\w+)"), re.compile("0x([0-9a-z]{4})")]
SETTINGS_FILE = os.path.dirname(sys.argv[0]) + os.sep + 'config.json'


# 
class DeviceCountSet(dict):
	# Warning: this class has behavior you may not expect.
	# This is because the overloaded __add__ is a mixture of add and overwrite
	def __init__(self, list):
		count = dict()
		for i in list:
			h = utils.create_hash(i)
			if type(i) == dict:
				count[utils.create_hash(i.items()[0])] = i.values()[0]
			elif h in count:
				count[h] += 1
			else:
				count[h] = 1
		super(DeviceCountSet, self).__init__(count)

	def __add__(self, other):
		newdic = dict(self)
		if isinstance(other, list) or isinstance(other, dict):
			for k in other:
				newdic[k] = 1
		else:
			for k,v in other.items():
				if k in newdic:
					if newdic[k] < v:
						newdic[k] = v
				else:
					newdic[k] = v
		return newdic

	def __sub__(self, other):
		newdic = dict(self)
		if isinstance(other, list) or isinstance(other, dict):
			for k in other:
				del newdic[k]
		else:
			for k,v in other.items():
				if k in newdic:
					del newdic[k]
		return newdic

# 
def help():
	help_message = """
	Usbkill is a simple program with one goal: quickly shutdown the computer when a USB is inserted or removed.
	Events are logged in program folder in file logs.txt
	You can configure a whitelist of USB ids that are acceptable to insert and the remove.
	The USB id can be found by running the command 'lsusb'.
	Settings can be changed program folder in file config.json
	In order to be able to shutdown the computer, this program needs to run as root.

	Options:
	    --help:             Show this help
	    --append:           To add a usb device to the whitelist, you need to run the program with the 
	                        '--append' flag, then insert a new usb device and wait 3-4 seconds.
	                        To add multiple usb devices, you need to repeat this procedure for each device separately.
	    --remove:           To remove a usb device from whitelist, you need to run the program with the '--remove' flag,
	                        then insert the usb device and wait 3-4 seconds. Each device is removed individually.       
	    --hiden:            Start program in hiden mode (without console).
	    --dont-shut-down:   Do not turn off the computer when a usb device is detected or disconnected
	    --version:          Print usbkill version and exit
	"""
	return help_message

# 
def lsusb_darwin():
	# Use OS X system_profiler (native and 60% faster than lsusb port)
	df = subprocess.check_output("system_profiler SPUSBDataType -xml -detailLevel mini", shell=True)
	if sys.version_info[0] == 2:
		df = plistlib.readPlistFromString(df)
	elif sys.version_info[0] == 3:
		df = plistlib.loads(df)

	def check_inside(result, devices):
		"""
			I suspect this function can become more readable.
		"""
		# Do not take devices with Built-in_Device=Yes
		try:
			result["Built-in_Device"]
		except KeyError:
		
			# Check if vendor_id/product_id is available for this one
			try:
				# Ensure vendor_id and product_id are present
				assert "vendor_id" in result and "product_id" in result

				try:
					vendor_id = DEVICE_RE[1].findall(result["vendor_id"])[0]
				except IndexError:
					# Assume this is not an standard vendor_id (probably apple_vendor_id)
					vendor_id = result["vendor_id"];

				try:
					product_id = DEVICE_RE[1].findall(result["product_id"])[0]
				except IndexError:
					# Assume this is not an standard product_id (probably apple_vendor_id)
					product_id = result["product_id"];

				# Append to the list of devices
				devices.append(vendor_id + ':' + product_id)

			except AssertionError: {}

		# Check if there is items inside
		try:
			# Looks like, do the while again
			for result_deep in result["_items"]:
				# Check what's inside the _items array
				check_inside(result_deep, devices)
					
		except KeyError: {}
		
	# Run the loop
	devices = []
	for result in df[0]["_items"]:
		check_inside(result, devices)
	return devices

# 
def lsusb_windows():
    devices = []
    REG_PATH = r'SYSTEM\CurrentControlSet\services\Disk\Enum'

    access_registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
    registry_key = winreg.OpenKeyEx(access_registry, REG_PATH, 0, winreg.KEY_READ)

    count, _ = winreg.QueryValueEx(registry_key, 'count')

    for i in range(0, count):
        value, regtype = winreg.QueryValueEx(registry_key, f'{i}')
        values = value.split('&')
        devices.append(values[1] + ':' + values[3])

    winreg.CloseKey(registry_key)

    return devices

# 
def lsusb():
	# A Python version of the command 'lsusb' that returns a list of connected usbids
	if CURRENT_PLATFORM.startswith("DARWIN"):
		# Use OS X system_profiler (native, 60% faster, and doesn't need the lsusb port)
		return DeviceCountSet(lsusb_darwin())
	# use register from 
	elif CURRENT_PLATFORM.startswith("WINDOWS"):
		return DeviceCountSet(lsusb_windows())
	else:
		# Use lsusb on linux and bsd
		return DeviceCountSet(DEVICE_RE[0].findall(subprocess.check_output("lsusb", shell=True).decode('utf-8').strip()))

# 
def load_settings(filename):
	if not os.path.exists(os.path.dirname(filename)):
		os.mkdir(os.path.dirname(filename))
	
	# If config file does not exists write base config
	if not os.path.exists(filename):
		settings = utils.BASE_CONFIG
		# Save base config 
		utils.dump_json(filename, settings)
	else:
		settings = utils.load_json(filename)

	return settings

# 
def startup_checks(settings):
	for arg in sys.argv[1:]:
		if arg in ('-h', '--help'):
			sys.exit(help())
		
		elif arg in ('-v', '--version'):
			sys.exit('USB kill version: %s' % __version__) 
		
		elif arg in ('--append', '--remove', '--hiden', '--dont-shut-down'):
			continue
		
		else:
			sys.exit("[ERROR] Argument not understood. Can only understand -h/--help")

	if not os.path.exists(settings['log_file']):
		with open(settings['log_file'], mode='w') as file:
			file.write('[INFO] created log file %s\n' % utils.dttm_now())
		
		if settings['first_boot']:
			print('[WARNING] Log file does not exists. Log file will be created during program execution.')
			settings['first_boot'] = False		
		else:
			print('[WARNING] Log file does not exists. Maybe someone deleted the log file.')

		utils.dump_json(settings['settings_file'], settings)
				
	executable = sys.executable
	command = __file__ + ' ' +  ' '.join(sys.argv[1:])
	# Check if program is run as root, else exit.
	# Root is needed to power off the computer.
	if CURRENT_PLATFORM.endswith('WINDOWS'):
		# If program sterted without administrator rights automatically start new program with them
		if not ctypes.windll.shell32.IsUserAnAdmin():
			ctypes.windll.shell32.ShellExecuteW(None, 'runas', executable, command, None, 1)
			sys.exit("[INFO] Restart program with administrator rights.") # Close current process
	
	elif not os.geteuid() == 0:
		# If program sterted without root rights automatically start new program with them
		os.system('sudo %s %s' % (executable, command))
		# Close current process
		sys.exit("[INFO] Restart program with root rights.")

	# Warn the user if he does not have FileVault
	if CURRENT_PLATFORM.startswith("DARWIN"):
		try:
			# fdesetup return exit code 0 when true and 1 when false
			subprocess.check_output(["/usr/bin/fdesetup", "isactive"])
		except subprocess.CalledProcessError:
			sys.exit("[NOTICE] FileVault is disabled. Sensitive data SHOULD be encrypted.")

	print("[INFO] Program started successfuly")

# 
def kill_computer(settings):
	# Log what is happening:
	utils.logging.warning("[%s] Detected a USB change. Killing the computer..." % utils.dttm_now())

	if not CURRENT_PLATFORM.endswith('WINDOWS'):
		os.system("sync")

	# *Wipe ram 
	if settings['do_wipe_ram']:
		os.system(settings['wipe_ram_cmd'])
	
	# *Wipe swap file
	if settings['do_wipe_swap']:
		os.system(settings['wipe_swap_cmd'])

	if sttings['do_outher_command']:
		os.system(settings['outher_command'])
	
	if '--dont-shut-down' not in settings['flags']: # (Use argument --dont-shut-down to prevent a shutdown.)
		# Finally poweroff computer immediately
		if CURRENT_PLATFORM.startswith("DARWIN"):
			# OS X (Darwin) - Will halt ungracefully, without signaling apps
			os.system("killall Finder ; killall loginwindow ; halt -q")
		elif CURRENT_PLATFORM.endswith("BSD"):
			# BSD-based systems - Will shutdown
			os.system("shutdown -h now")
		elif CURRENT_PLATFORM.endswith('WINDOWS'): 
			# Shutdown computer
			os.system("shutdown -s -t 0")
		else:
			# Linux-based systems - Will shutdown
			os.system("poweroff -f")
		
		sys.exit(0)

# 
def loop(settings):
	# Main loop that checks every 'sleep_time' seconds if computer should be killed.
	# Allows only whitelisted usb devices to connect!
	# Does not allow usb device that was present during program start to disconnect!
	start_devices = lsusb()
	acceptable_devices = start_devices + settings['whitelist']
	
	# Write to logs that loop is starting:
	utils.logging.info(
		"[%s] Started patrolling the USB ports every %s seconds..."  % (utils.dttm_now(), settings['sleep_time']))

	while True:
		# List the current usb devices
		current_devices = lsusb()
		# Check that all current devices are in the set of acceptable devices
		# and their cardinality is less than or equal to what is allowed 
		for device, count in current_devices.items():
			if '--append' in settings['flags'] and device not in acceptable_devices:
				settings['whitelist'].append(device)
				settings['flags'].remove('--append')
				utils.logging.info('[%s] Added new usb device. Hash: %s' % (utils.dttm_now(), device))
				print('[INFO] Added new usb device. hash: %s' % device)
				acceptable_devices.update({device: 1})
				utils.dump_json(SETTINGS_FILE, settings)
				continue
			if '--remove' in settings['flags'] and device not in start_devices:
				if device in settings['whitelist']:
					settings['whitelist'].remove(device)
					settings['flags'].remove('--remove')
					utils.logging.info('[%s] Removed usb device. Hash: %s' % (utils.dttm_now(), device))
					print('[INFO] Removed usb device. hash: %s' % device)
					utils.dump_json(SETTINGS_FILE, settings)
				else:
					utils.logging.warning('[%s] Unknown usb device to remove. Hash: %s' % (utils.dttm_now(), device))
					print('[WARNING] Unknown usb device to remove. hash: %s' % device)
					print('[WARNING] Pull out the unknown usb device within a 5 seconds otherwise the computer will be shutdown.')
					time.sleep(5)
				continue

			if device not in acceptable_devices:
				# A device with unknown usbid detected
				utils.logging.warning('[%s] Detected unknown usb device (%s)' % (utils.dttm_now(), device))
				kill_computer(settings)
			if count > acceptable_devices[device]:
				# Count of a usbid is larger than what is acceptable (too many devices sharing usbid)
				utils.logging.warning('[%s] Detected unknown usb devices' % utils.dttm_now())
				kill_computer(settings)

		# Check that all start devices are still present in current devices
		# and their cardinality still the same 
		for device, count in start_devices.items():
			if device not in current_devices:
				# A usbid has disappeared completely
				utils.logging.warning('[%s] Detected disappeared usb devices (%s)' % (utils.dttm_now(), device))
				kill_computer(settings)
			if count > current_devices[device]:
				# Count of a usbid device is lower than at program start (not enough devices for given usbid)
				utils.logging.warning('[%s] Detected not enough devices' % utils.dttm_now())
				kill_computer(settings)

		time.sleep(settings['sleep_time'])

# 
def main():
	# Shows the script logo by running the "logo.py" script in a separate process
	if __file__.endswith('.pyw'):
		if '--auto-reboot' not in sys.argv:
			subprocess.check_call(['python', os.path.join(os.path.dirname(__file__), 'logo.py')])
	# If script usbkill.py started with flag --hiden start new script usbkill.pyw   
	elif '--hiden' in sys.argv:
		if '--auto-reboot' not in sys.argv:
			subprocess.check_call(['python', os.path.join(os.path.dirname(__file__), 'logo.py')])
		
		sys.argv.remove('--hiden')
		executable = sys.executable.replace('python', 'pythonw')
		command = __file__ + 'w ' + ' '.join(sys.argv[1:])
		
		if CURRENT_PLATFORM.endswith('WINDOWS'):
			ctypes.windll.shell32.ShellExecuteW(None, 'runas', executable, command, None, 1)
			# Close current process
			sys.exit("[INFO] Restart program with administrator rights.")
		else:
			os.system('sudo %s %s' % (executable, command))
			# Close current process
			sys.exit("[INFO] Restart program with root rights.")
	# If started script usbkill.py without flag --hiden
	elif '--auto-reboot' not in sys.argv:
		print(utils.LOGO)

	settings = load_settings(SETTINGS_FILE)
	settings['settings_file'] = SETTINGS_FILE
	settings['flags'] = sys.argv[1:]

	# Checks startup params
	startup_checks(settings)
	# Initialization logging in module utils
	utils.logging.basicConfig(level=utils.logging.NOTSET, filename=settings['log_file'])
	# Binding signals to custom exit handlers
	utils.bind_signals(CURRENT_PLATFORM)
	# Start main loop
	loop(settings)

if __name__=="__main__":
	main()