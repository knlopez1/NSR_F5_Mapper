import serial
import time
from FieldConverter import fieldReading, zeroReading
import datetime
import os.path
import statistics

motherDirectory = 'C:/Users/NSR/Desktop/Quspin Probe Stuff/Stuff/Non-Junk/DualAxisTest'

###################### creates a folder for the data; if the folder exists already, adds an index 

Date = datetime.datetime.fromtimestamp(time.time()).strftime('%m_%d')
FolderName = Date + '_DualAxisTest'

def checkI(j):
	if os.path.isdir(os.path.join(motherDirectory, FolderName + "_" + str(j))) == False:
		return j
	else: 
		return checkI(j+1)

if os.path.isdir(os.path.join(motherDirectory, FolderName)) == False:
	os.makedirs(os.path.join(motherDirectory, FolderName))
else:
	index = checkI(2)
	FolderName = FolderName + "_" + str(index)
	os.makedirs(os.path.join(motherDirectory, FolderName))

#######################

RawTargetY = open(os.path.join(motherDirectory, FolderName, "YRawData.txt"), "w+") # Defines paths to folders in which we write raw Y- and Z-data
RawTargetZ = open(os.path.join(motherDirectory, FolderName, "ZRawData.txt"), "w+")
ProcTargetY = open(os.path.join(motherDirectory, FolderName, "YData.txt"), "w+")
ProcTargetZ = open(os.path.join(motherDirectory, FolderName, "ZData.txt"), "w+")


# .0003 hrs ~ 1 sec /// .0167 hrs ~ 1 min

TestDurationHrs = 23.75										# Specifies test duration in hours. 
TestDuration = TestDurationHrs*60*60						# Test duration in seconds

def saveData(axis, data):
	ts = time.time()
	st = datetime.datetime.fromtimestamp(ts).strftime('%m/%d/%Y %H:%M:%S')
	string = 'Time: ' + str(st) + '\n'
	for i in data.split():
		string = string + str(i) + '\n'
	string = string + "######################################\n"
	if axis == 'y':
		Target = RawTargetY
	elif axis == 'z':
		Target = RawTargetZ
	Target.write(string)
	return

def DataProc():
	Header = 'Timestamp:\tpT Value:\tStandard Dev:\n'
	if ProcTargetY.read() == '':
		ProcTargetY.write(Header)
	ydataPackets = open(os.path.join(motherDirectory, FolderName, "YRawData.txt"), "r").read().split('######################################\n')
	for packet in ydataPackets:
		packList = []											# Now the program iterates through the data streams
		for line in packet.split('\n')[1:-2]:					# It splits the streams into individual data lines (1 line = 1 reading)
			packList = packList + [fieldReading(line)]			# Readings are converted into a readable pT value, then added to our list of values
		if packList == []:
			pass
		else:
			RawHeader = (packet.split('\n')[0]).split(' ')		# This line grabs the Raw Data Stream header, which contains important info (coords, time)
			time = RawHeader[2]									# The time variable (HOUR:MINUTE:SECOND) is the third elt in the RawHeader list. 
																# Note date is the second term and can be added if desired
			transmission = time + '\t' + str(round((statistics.mean(packList)),2)) + '\t\t' + str(round((statistics.pstdev(packList)),2)) + '\n'
			ProcTargetY.write(transmission)							# Appends a line to the Processed Data file, containing all the desired info

	if ProcTargetZ.read() == '':
		ProcTargetZ.write(Header)
	zdataPackets = open(os.path.join(motherDirectory, FolderName, "ZRawData.txt"), "r").read().split('######################################\n')
	for packet in zdataPackets:
		packList = []											# Now the program iterates through the data streams
		for line in packet.split('\n')[1:-2]:					# It splits the streams into individual data lines (1 line = 1 reading)
			packList = packList + [fieldReading(line)]			# Readings are converted into a readable pT value, then added to our list of values
		if packList == []:
			pass
		else:
			RawHeader = (packet.split('\n')[0]).split(' ')		# This line grabs the Raw Data Stream header, which contains important info (coords, time)
			time = RawHeader[2]									# The time variable (HOUR:MINUTE:SECOND) is the third elt in the RawHeader list. 
																# Note date is the second term and can be added if desired
			transmission = time + '\t' + str(round((statistics.mean(packList)),2)) + '\t\t' + str(round((statistics.pstdev(packList)),2)) + '\n'
			ProcTargetZ.write(transmission)							# Appends a line to the Processed Data file, containing all the desired info


def flush():
	ser.flushInput()
	ser.flushOutput() 

def zeroExtract(lst):									# Takes a list of raw zero readings and extracts the most recent field zero values
	Bybool = False
	Bzbool = False
	B0bool = False
	By = 0
	Bz = 0
	B0 = 0
	index = len(lst)
	while (index > 1) and ((By == 0) or (Bz == 0) or (B0 == 0)):
		index = index - 1
		if not (lst[index].decode("utf-8"))[0] == '~':
			line = 'zero'
		else:
			line = zeroReading(lst[index].decode("utf-8"))
		if (line[0] == 'By') and (Bybool == False):
			Bybool = True
			By = line[1]
		elif (line[0] == 'Bz') and (Bzbool == False):
			Bzbool = True
			Bz = line[1]
		elif  (line[0] == 'B0') and (B0bool == False):
			B0bool = True
			B0 = line[1]
		else:
			pass
	return [By, Bz, B0]

def autocheck(index):											# # # This function checks the data buffer to see if the autostart is completed. 
	OVERRIDE = True												# Set to TRUE to skip Autostart process (for debugging)
	if OVERRIDE == True:
		print("Skipped Autocheck.")
		return
	time.sleep(15)
	print("Attempt " + str(index))								# Prints attempt number
	if index > 5:
		print("Error: Auto Start Unsuccessful!")				# If attempt number exceeds five, the program will give up. 
		sys.exit()
	else:
		pass													#Now we start from the assumption that none of the LED lights are on. 
	One = False													#LED One - Laser On
	Two = False													#LED Two - Cell Temperature Lock Off/On
	Three = False												#LED Three - Laser Lock Off/On

	num = ser.in_waiting										#This block reads the buffer. Num is the number of bits waiting in the buffer.
	print("Buffer Size: " + str(num))							#Buffer length is printed for fun. 
	data = ser.readlines(num)									#Loads the buffer into a variable as a list of strings
	ser.flushInput()											
	ser.flushOutput()											#Input and Output flushed for good measure. We want to avoid repeats. 
	#print(data)
	for i in data:												#This block hunts for the markers signifying LED activation and checks them one by one			
		if i == b'|11\r\n':										#It runs through the data line by line and turns a variable to true if it finds
			One = True 												#the correct corresponding marker. 
		elif i == b'|21\r\n':
			Two = True
		elif i == b'|31\r\n':
			Three = True
		else:
			pass
	if ((One == True) and (Two == True) and (Three == True)):	#If all markers are tripped, it prints a success message and we can move on. 
		print("Auto Start Successful!")
		pass
	else:														#If not all markers are tripped, wait 20 seconds, index to the next attempt, and run through autocheck again
		time.sleep(20)
		autocheck(index + 1)
		pass	

with serial.Serial(port='COM3',baudrate=115200,timeout=1) as ser:
	print("Connection established. Beginning autostart.")
	flush()												# Clears buffers for good measure. 
	ser.write(str.encode(">"))							# Tells sensors: "Begin Autostart"
	autocheck(1)
	print("Begin field zero.")
	
	ser.write(str.encode("B"))							# Tells sensors: "Dual Axis Mode"
	ser.write(str.encode("D"))							# 				 "Field Zero ON"	
	
	time.sleep(15)										# Waits for field to zero. 
	flush()
	time.sleep(5)										# Gathers data for field zero reading. 

	bufferSize = ser.in_waiting
	zeroValues = ser.readlines(bufferSize)
	ser.write(str.encode("E"))							# "Field Zero OFF"

	finalZero = zeroExtract(zeroValues)
	print("Field zero successful. Field zero values:")
	print(finalZero)
	finalZeroString = str(finalZero)
	open(os.path.join(motherDirectory, FolderName, "FieldZeroValues.txt"), "a").write('[B0, By, Bz]' + '\n' + finalZeroString)  # Opens a file path and writes to save the field zero values.
																										# I don't know why it wasn't working if I put this with the other file names.
	print("Begin calibration.")

	ser.write(str.encode("9"))							# "Calibrate"

	time.sleep(5)
	print("Calibration successful.")

	ser.write(str.encode("7"))							# Print ON Command

	time.sleep(10)
	flush()

	startTime = time.time()
	endTime = startTime + TestDuration

	print(startTime)
	print(time.time())
	print(endTime)

	while time.time() < endTime:
		ser.write(str.encode("@"))					# Print Mode: Y
		time.sleep(.5)
		flush()
		time.sleep(.5)
		bufferSize = ser.in_waiting												# Loads number of bits in buffer into a variable 'a'	
		ydata = ser.readlines(bufferSize)
		ystring = ""
		for i in ydata:															
			ystring = ystring + i.decode("utf-8")	# Loads data into a list to be processed and formatted
		saveData('y', ystring)
		ser.write(str.encode("?"))					# Print Mode: Z
		time.sleep(.5)
		flush()
		time.sleep(.5)
		bufferSize = ser.in_waiting												# Loads number of bits in buffer into a variable 'a'	
		zdata = ser.readlines(bufferSize)
		zstring = ""
		for j in zdata:															
			zstring = zstring + j.decode("utf-8")	# Loads data into a list to be processed and formatted
		saveData('z', zstring)
		print(time.time())
	#DataProc()
