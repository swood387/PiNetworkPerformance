import subprocess
import time
import os

import blinkt
# Raspberry Pi pin configuration:
RST = 24

# 128x64 display with hardware I2C:

#print 'Press Ctl-C to exit'

#functions
def getSnmpData (oid):

	try:
		data = subprocess.check_output("snmpget -v 1 -c mrtg 192.168.1.1 " + oid, shell = True)
	except subprocess.CalledProcessError as e:
		data = e
	else:
		data = "unhandled error"
	return data;

def getSnmpInt (oid):

	try:
		data = subprocess.check_output("snmpget -v 1 -c mrtg 192.168.1.1 " + oid, shell = True)
		data = data.split()
		data = data.pop()
	except:
		data = "0"
	return int(data)

def textRate (rate):
	rate = rate * 8 / 1024
	if rate < 1024:
		result = str(round(rate,1)) + ' kbps'
	else:
		result = str(round(rate/1000,1)) + ' mbps'
	return result


def show_graph(v):
	#blinkt.clear()
        #blinkt.set_brightness(0.04)
        #blinkt.set_pixel(7,100,100,0)
        #blinkt.show()
        #time.sleep(.25)
        blinkt.clear()
 	blinkt.set_brightness(0.04)
	#v = 100

	num_pixels = int(round((v)/12))
	print 'calculated pixels ' + str(num_pixels)
	if (v > 0) and (num_pixels == 0):
		num_pixels = 1

	if num_pixels > 8:
		num_pixels = 8
	print 'actual pixels ' + str(num_pixels)

	x = 0
	while (x < num_pixels):
		r, g, b = 0, 0, 155
		if x > 4:
			r, g, b = 155, 100, 0
		if x > 6:
			r, g, b = 155, 0, 0
		print 'x = ' + str(x) + ' r = ' + str(r) + ' g = ' + str(g) + ' b = ' + str(b)
		blinkt.set_pixel(x, r, g, b)
		x = x + 1
	blinkt.show()

#defines
oidInWan = '1.3.6.1.2.1.2.2.1.10.4'
oidOutWan = '1.3.6.1.2.1.2.2.1.16.4'

lastInBytes = getSnmpInt (oidInWan);
lastOutBytes = getSnmpInt (oidOutWan);
lastTime = time.time()

maxRateIn = 3750000
maxRateOut = 120000

#timed array vars
timerTime = time.time()
highestSpeedIn = 0
highestSpeedOut = 0
speedArrayIn = []
speedArrayOut = []
inMax = 0
outMax = 0

while (1):
	os.system('clear')
	now = time.time()
	elapsed = now - lastTime
	lastTime = now

	#calculate rates in and out
	inBytes = getSnmpInt (oidInWan)
	currInBytes = (inBytes - lastInBytes) / elapsed
	lastInBytes = inBytes

	outBytes = getSnmpInt (oidOutWan)
	currOutBytes = (outBytes - lastOutBytes) / elapsed
	lastOutBytes = outBytes

	#max rate last 24 hours calculations
	if currInBytes > highestSpeedIn:
		highestSpeedIn = currInBytes
	if currOutBytes > highestSpeedOut:
		highestSpeedOut = currOutBytes

	if now > timerTime + 3600:
		print '-----------------------------------------------------------------  time expired'
		timerTime = now

		speedArrayIn.append (highestSpeedIn)
		if len (speedArrayIn) > 23:
			del speedArrayIn[0]
		inMax = max(speedArrayIn)

		speedArrayOut.append (highestSpeedOut)
                if len (speedArrayOut) > 23:
                        del speedArrayOut[0]
		outMax = max(speedArrayOut)

		highestSpeedIn = 0
		highestSpeedOut = 0

		#test output
		for inSpd in speedArrayIn:
			print '--- ' + str(inSpd)
		print 'inMax ' + str(inMax)

	#adjust these in each loop in case we find a faster speed
	inMax = max(inMax, highestSpeedIn)
	inPercentage = int(round((currInBytes/12500000*100)))
	outMax = max(outMax, highestSpeedOut)
	outPercentage = int(round((currOutBytes/1250000*100)))

	#print str(now) + '    ' + str(timerTime)
	print 'In: ' + textRate(currInBytes) + '\tOut: ' + textRate(currOutBytes) + '\tElapsed ' + str(round(elapsed,2)) + '\t\tInMax ' + textRate(inMax) + '\tOutMax ' + textRate(outMax)
	#print 'Hi In ' + str(highestSpeedIn) + '   Hi Out ' + str(highestSpeedOut)
	print 'Download Percentage: ' + str(inPercentage) + '%' + '\tUpload Percentage: ' + str(outPercentage) + '%'

	#
	# Turn on Blinkit
	#


	graph_percentage = inPercentage
	show_graph(graph_percentage)

	time.sleep(5)
