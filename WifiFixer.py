# Turns Wi-Fi off then on.  Windows only.  Must be run as admin.

import os
import subprocess
from time import sleep, time

def pingGoogle(use_alternate_ip = False):
	# Ping Google, return 1 (True) for pass and 0 (False) for fail
	
	# If use_alternate_ip, use 8.8.4.4
	if not use_alternate_ip:
		google_ip = '8.8.8.8'
	else:
		google_ip = '8.8.4.4'
	
	# Ping Google once and get response
	response = os.system("ping -n 1 {}".format(google_ip))
	# print response

	# Check the response
	if response == 0:
		# print 'Router ping successful'
		return 1
	else:
		# print 'Router ping failed!'
		return 0
		
def enableWifi():		
	# Enable Wi-Fi
	subprocess.check_output('netsh interface set interface "Wi-Fi" enabled')

def disableWifi():
	# Disable Wi-Fi
	subprocess.check_output('netsh interface set interface "Wi-Fi" disabled')

def resetWifi():
	# Disable Wi-Fi, sleep, Enable Wi-fi
	print 'Turning off Wi-Fi'
	disableWifi()
	print 'Wi-Fi off, sleeping...'
	sleep(3)
	print 'Turning on Wi-Fi'
	enableWifi()
	print 'Wi-Fi ON'

if __name__ == '__main__':
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
		
