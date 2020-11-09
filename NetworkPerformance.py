import subprocess
import time
import os


print 'Press Ctl-C to exit'

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


#defines
oidInWan = '1.3.6.1.2.1.2.2.1.10.4'
oidOutWan = '1.3.6.1.2.1.2.2.1.16.4'

lastInBytes = getSnmpInt (oidInWan);
lastOutBytes = getSnmpInt (oidOutWan);
lastTime = time.time()

maxRateIn = 12500000
maxRateOut = 1250000

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

	time.sleep(5)
