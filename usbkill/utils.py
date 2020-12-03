import os
import sys
import json
import signal
import hashlib
import logging
import datetime

try:
	import winreg
except ModuleNotFoundError:
	pass


LOGO = ""\
	"             _     _     _ _ _  \n"\
	"            | |   | |   (_) | | \n"\
	"  _   _  ___| |__ | |  _ _| | | \n"\
	" | | | |/___)  _ \| |_/ ) | | | \n"\
	" | |_| |___ | |_) )  _ (| | | | \n"\
	" |____/(___/|____/|_| \_)_|\_)_)\n"


BASE_CONFIG = dict(
	first_boot=True, # Need from define is first boot or not.
	sleep_time=1, # Usb ports update interval.
	do_wipe_ram=False, # Boolean variable. If the value is True, before shutting down the computer, execute the command written under the "wipe_ram_swap" key
	wipe_ram_cmd=None, # cmd command. 
	# wipe_ram_cmd = r"%windir%\system32\rundll32.exe advapi32.dll,ProcessIdleTasks" # Base command from windows. Release system memory when certain programs was don't properly closed.
	do_wipe_swap=False, # Boolean variable. The principle of operation is the same as that of do_wipe_ram
	wipe_swap_cmd=None, # cmd command.
	# Base command from windows. Sets a flag in register to clear the swap file on shutdown.
	# wipe_swap_cmd = r'REG ADD "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management" /v ClearPageFileAtShutdown /t REG_DWORD /d 0x00000001 /f'
	do_outher_command=False, # Boolean variable. If the value is True, executes an additional command.
	outher_command=None, # cmd command.
	whitelist=[], # List hashed values allowable devices 
	log_file=os.path.dirname(sys.argv[0]) + os.sep + 'logs.txt') # 

# 
def dttm_now():
	return datetime.datetime.now()
# 
def dump_json(filename, data):
	with open(filename, mode = 'w') as file:
		json.dump(data, file, indent=4)

# 
def load_json(filename):
	with open(filename, mode = 'r') as file:
		return json.loads(file.read())

# 
def exit_handler(signum, frame):
	logging.error("[%s] Signal handler called with signal %s. Exiting..." % (dttm_now(), signum))	
	sys.exit(0)

# 
def bind_signals(platform):
	"""
	On Windows, signal() can only be called with
	SIGABRT, SIGFPE, SIGILL, SIGINT, SIGSEGV, SIGTERM, or SIGBREAK. 
	A ValueError will be raised in any other case. 
	Note that not all systems define the same set of signal names; 
	an AttributeError will be raised if a signal name is not defined as SIG* module level constant.
	"""
	if platform.endswith('WINDOWS'):
		for sig in [signal.SIGABRT, signal.SIGINT, signal.SIGTERM, signal.SIGBREAK]:
			signal.signal(sig, exit_handler)

	else:
		for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGQUIT]:
			signal.signal(sig, exit_handler)

# 
def create_hash(string):
	b = string.encode()
	h = hashlib.sha256()
	h.update(b)
	# Slows down the hashing of the device serial number. 
	for _ in range(10000): 
		h.update(h.digest()+b)
	return h.hexdigest()
