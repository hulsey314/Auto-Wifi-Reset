# WifiFixer v.1.0.0
# Monitors WiFi to check if internet is connected. Resets Wifi adapter
# when no connection is found
# Windows only.  Must be run as admin

import os
import sys
import subprocess
import re
from time import sleep, time

def pingGoogle(use_alternate_ip = False):
	# Ping Google, return True for pass or False for fail
	# If use_alternate_ip, use 8.8.4.4
	if use_alternate_ip:
		google_ip = '8.8.4.4'
	else:
		google_ip = '8.8.8.8'
	
	# Ping Google once and get response
	startupinfo = subprocess.STARTUPINFO()
	startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
	ping_output = subprocess.Popen(['ping', google_ip, '-n', '1'],startupinfo=startupinfo, stdout=subprocess.PIPE).stdout.read()

	# Use regex to compile ping_output into response list
	regex = re.compile(r'from\s(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b).*bytes=(\d*).*time=(\d*).*TTL=(\d*)')
	response = regex.findall(ping_output)

	# Check response from Google
	if response:
		print 'Google ping successful'
		return True
	else:
		print 'Google ping failed!'
		return False
		
def enableWifi():		
	# Enable Wi-Fi
	subprocess.Popen('netsh interface set interface "Wi-Fi" enabled', startupinfo=startupinfo)

def disableWifi():
	# Disable Wi-Fi
	subprocess.Popen('netsh interface set interface "Wi-Fi" disabled', startupinfo=startupinfo)
	
def resetWifi():
	# Disable Wi-Fi, sleep, Enable Wi-fi
	print 'Turning off Wi-Fi'
	disableWifi()
	print 'Wi-Fi off, sleeping...'
	sleep(3)
	print 'Turning on Wi-Fi'
	enableWifi()
	print 'Wi-Fi ON'
	
def monitorWifi():
	# Ping Google periodically to check for wifi issues, sleep after
	# failing too many times
	print 'Monitoring Wi-Fi...'
	
	# Sleep after resetting too many times, when WiFi is not available
	fail_count = 0
	fail_limit = 3
	fail_time_limit = 10 * 60
	fail_start_time = time()
	
	# Set delay between checks in seconds
	check_delay = 5
	while True:
		# Reset fail_count to 0 after fail_time_limit
		if time() - fail_start_time >= fail_time_limit:
			fail_count = 0
			fail_start_time = time()
		
		# Ping Google and check response
		if pingGoogle() == False:
			# Ping failed, sleep then recheck
			print 'Google ping failed - retrying (1)'
			sleep(2)
			if pingGoogle(use_alternate_ip = True) == False:
				# Ping failed again, try once more on 2nd ip
				print 'Google ping failed - retrying (2)'
				sleep(2)
				if pingGoogle(use_alternate_ip = True) == False:
					# Stop resetting Wi-Fi after fail_limit for a while
					fail_count += 1
					if fail_count > fail_limit:
						# Too many fails
						sleep_time = fail_time_limit - (time() - fail_start_time)
						print 'Sleeping {}'.format(sleep_time)
						sleep(sleep_time)
						fail_start_time = time()
						fail_count = 0
					print 'Google ping failed - resetting Wi-Fi...'
					# Ping failed 3x, reset Wi-Fi NIC
					resetWifi()
					print 'Wi-Fi reset!'
					# Wait for Wi-Fi to reconnect to network then check
					print 'Waiting to reconnect to internet...'
					sleep(10)
					if pingGoogle():
						print 'Reset fixed the issue'
					else:
						print 'Reset failed to fix the issue'
				else:
					print 'Router ping passed (Retry 2)'
			else:
				print 'Router ping passed (Retry 1)'
		else:
			print 'Router ping passed'
				
		# Sleep before next ping check
		sleep(check_delay)

startupinfo = None
startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


if __name__ == '__main__':
	# Allow program to be run in monitor mode or just as a reset
	if len(sys.argv) == 2:
		# Check for reset argument
		if sys.argv[1] == 'reset':
			# Reset Wifi
			resetWifi()
			print 'Wi-Fi reset!'
			# Wait for Wi-Fi to reconnect to network then check
			print 'Waiting to reconnect to internet...'
			sleep(10)
			# Allow retry_limit retries to wait for wifi to reconnect
			retry_limit = 2
			for _ in xrange(retry_limit):
				if pingGoogle():
					print 'Reset fixed the issue'
					# Break when internet is back (pingGoogle returns True)
					break
				else:
					# Retry after retry_delay_time seconds
					retry_delay_time = 10
					print 'Reset failed to fix the issue, retrying in {}s'.format(retry_delay_time)
					sleep(retry_delay_time)
		else:
			# Print error if argument is not recognized
			print 'ERROR: Argument not recognized ({})'.format(sys.argv[1])
	else:
		# If no arguements are passed, start monitoring
		print 'Monitor mode beginning...'
		monitorWifi()
