import sys
import serial
import math
import os.path
from datetime import datetime
from datetime import timedelta
import time
import statistics as stat

AxisMode = ""  # This will have something to do with axis orientation etc. Will likely be embedded in the premap file

# Parameters for Map Information

mapTitle = "default"  # leave "default" for default map naming scheme
operatorComments = ""  # leave your comments here

# Parameters for the Motors

cooldown = 1  # number of seconds that motors will 'cool down' after movement to allow for good measurement
                # we don't want probe wobble represented in the data

motor = serial.Serial('COM1')  # initializes the serial port for the motors
motor.write(str.encode('DRIVE0011:'))  # enables x and y axis motors

motion_profile = ("MA XX00:",  # creates the motion profile list that will be sent to the motors
                  "A ,,10,10:",
                  "AA ,,5.000000,5.000000:",
                  "AD ,,10,10:",
                  "ADA ,,5.000000,5.000000:",
                  "V ,,4,3:",
                  "",  # this item in the list defines the distance the motor travels, will be filled in later
                  "MC XX00:")
motion_profile = list(motion_profile)

# Initialization of variables from pre-image header ; ; ;

preImageFilename = "simple_50x50_05.30.2020_14.44.24.txt"  # the name of the pre-image file (including .txt)
preImageLocation = "C:/Users/lsead/Desktop/CEEM Remote/MapPlanner/TestFolder"  # the path to the folder in which the pre-image is located
dataDestination = "C:/Users/lsead/Desktop/CEEM Remote/MapPlanner/TestFolder"  # path to where you want results spat out

preImage = (open(os.path.join(preImageLocation, preImageFilename), "r")).read()

header = preImage.split("###############################")[0]  # separates pre-image header and command list
commands = preImage.split("###############################")[1]

for line in header.split("\n"):  # Initializing relevant variables from header of data file
    if line[
       :17] == "Plate Dimensions:":  # Reads header line-by-line and reads off values of variables that depend on pre-image parameters
        plateDim = line[18:-4]
    elif line[:15] == "Map Resolution:":
        resolution = line[-5:]
    elif line[:17] == "Sampling Pattern:":
        samplingPattern = line[18:]
    elif line[:12] == "Data Scheme:":
        scheme = line[13:]
    elif line[:14] == "X Cell Length:":
        xlen = float(line[15:-3])
    elif line[:14] == "Y Cell Length:":
        ylen = float(line[15:-3])  # ylen and xlen are the distance in meters of a resolution 'step' in either direction

date_time = (datetime.now()).strftime(
    "%m.%d.%Y_%H.%M.%S")  # grabs the current date and time for the purpose of file-naming

if mapTitle == "default":
    mapTitle = samplingPattern + "_" + resolution + "_" + date_time + "_MAP"
    # default map title will depend on sampling pattern used, resolution, and the current time

finalDest = os.path.join(dataDestination, mapTitle)
os.mkdir(finalDest)  # this function creates a directory for all the data to go into

# Initializing Data Files

info_file = open(os.path.join(finalDest, "info.txt"), "w+")  # A file containing information on the mapping run
master_data = open(os.path.join(finalDest, "master.txt"), "w+")  # Time series that will contain everything, for good measure
master_head = "Position:\tAxis:\t\t\tField (pT):\t\t\tField stdev:\n"
master_data.write(master_head)
master_raw = open(os.path.join(finalDest, "master_raw.txt"), "w+")


# Note on data files;
#   master.txt will contain every single possible piece of data
#   if 'data scheme' is x-linear, we will also include an additional file for each plate-line in the x-axis
#   this will split up the data into manageable chunks for the purpose of data analysis etc
#   possible other options may include bi-x-linear or n-x-linear to bunch n lines together (might be useful depending on line dimensions)

line_head = "Timestamp:\t\tPosition:\tYField (pT):\t\tYField stdev:\t\tZField (pT):\t\tZField stdev:\n"
if scheme == "x-linear":  # Creates a text file for each line of measurements by the y-axis
    global line_dict
    line_dict = []
    for i in range(1 + int((resolution.split("x"))[1])):
        line_dict = line_dict + [open(os.path.join(finalDest, ("line" + str(i) + ".txt")), "w+")]
        line_dict[i].write(line_head)

# Position Initialization

global coordX
global coordY

coordX = 0  # current coordinates in X and Y direction for purposes of data management
coordY = 0


# Motor Movement Functions

def MoveX(s):  # expects s (steps)
    dist0010 = s * xlen * 4096 / 2  # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    dist0001 = 0
    motion_profile[6] = "D ,," + str(dist0010) + "," + str(dist0001) + ":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    global coordX
    coordX = coordX + s
    time.sleep(cooldown)


def MoveY(s):  # expects s (steps)
    dist0010 = 0
    dist0001 = s * ylen * 4096 / 2  # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    motion_profile[6] = "D ,," + str(dist0010) + "," + str(dist0001) + ":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    global coordY
    coordY = coordY + s
    time.sleep(cooldown)


# This is here in case we want to move both motors at the same time
def MoveXY(sX, sY):  # expects sX and sY inputs (steps to move in x and y direction, respectively)
    dist0010 = sX * xlen * 4096 / 2
    dist0001 = sY * ylen * 4096 / 2
    motion_profile[6] = "D ,," + str(dist0010) + "," + str(dist0001) + ":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0011:"))
    global coordX
    global coordY
    coordX = coordX + sX
    coordY = coordY + sY
    time.sleep(cooldown)


def Measure():          # takes a .5-second burst of measurements in
    probe.write(str.encode("@"))  # Print Mode: Y
    time.sleep(.5)
    flush()
    time.sleep(.5)
    bufferSize = probe.in_waiting  # Loads number of bits in buffer into a variable 'a'
    ydata = probe.readlines(bufferSize)
    ystring = ""
    for i in ydata:
        ystring = ystring + i.decode("utf-8")  # Loads data into a list to be processed and formatted
    saveRaw('Y', ystring)
    probe.write(str.encode("?"))  # Print Mode: Z
    time.sleep(.5)
    flush()
    time.sleep(.5)
    bufferSize = probe.in_waiting  # Loads number of bits in buffer into a variable 'a'
    zdata = probe.readlines(bufferSize)
    zstring = ""
    for i in zdata:
        zstring = zstring + i.decode("utf-8")  # Loads data into a list to be processed and formatted
    saveRaw('Z', zstring)

            # note that with this arrangement we can expect 2 seconds per data point

def RotateTo():
    # will have to handle rotation given axis selection and other map data

def ZeroX():                                        #### We need to figure out what to do with these before we run
    global coordX                                               ### any maps.
    coordX = 0

def ZeroY():
    global coordY
    coordY = 0

# Probe Peripheral Functions

def flush():
    probe.flushInput()
    probe.flushOutput()

# translates raw field reading into a picotesla value
def fieldReading(read):             # input is a raw string from probe buffer
	bucket = read[1:]
	bucket = float(bucket)
	bucket = bucket - 8388608
	bucket = bucket * 0.01
	return (round(bucket,2)) #+ " pT"

# translates a raw zero field reading into a picotesla value
def zeroReading(read):
	if (read[2]) == '7':
		axis = 'Bz'
	elif (read[2]) == '8':
		axis = 'By'
	elif (read[2]) == '9':
		axis = 'B0'
	else:
		axis = '?'
	try:
		bucket = float(read[3:])
	except:
		return "Error: Not a float."
	bucket = bucket - 32768
	final = [axis,round(bucket,2)]
	return final

# Goes through the buffer and reads off most recent field zeroing values.
def zeroExtract(lst):  # Takes a list of raw zero readings and extracts the most recent field zero values
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
        elif (line[0] == 'B0') and (B0bool == False):
            B0bool = True
            B0 = line[1]
        else:
            pass
        return [By, Bz, B0]

def autocheck(index):  # # # This function checks the data buffer to see if the autostart is completed.
    print("Attempt " + str(index))  # Prints attempt number
    if index > 5:
        print("Error: Auto Start Unsuccessful!")  # If attempt number exceeds five, the program will give up.
        sys.exit()
    else:
        pass  # Now we start from the assumption that none of the LED lights are on.
    One = False  # LED One - Laser On
    Two = False  # LED Two - Cell Temperature Lock Off/On
    Three = False  # LED Three - Laser Lock Off/On

    num = probe.in_waiting  # This block reads the buffer. Num is the number of bits waiting in the buffer.
    #print("Buffer Size: " + str(num))  # Buffer length is printed for fun.
    data = probe.readlines(num)  # Loads the buffer into a variable as a list of strings
    flush()
    # Input and Output flushed for good measure. We want to avoid repeats.
    # print(data)
    for i in data:  # This block hunts for the markers signifying LED activation and checks them one by one
        if i == b'|11\r\n':  # It runs through the data line by line and turns a variable to true if it finds
            One = True  # the correct corresponding marker.
        elif i == b'|21\r\n':
            Two = True
        elif i == b'|31\r\n':
            Three = True
        else:
            pass
    if ((One == True) and (Two == True) and (
            Three == True)):  # If all markers are tripped, it prints a success message and we can move on.
        print("Auto Start Successful!")
        pass
    else:  # If not all markers are tripped, wait 20 seconds, index to the next attempt, and run through autocheck again
        time.sleep(20)
        autocheck(index + 1)
        pass


def saveRaw(ax, data):
    global coordX
    global coordY
    crd = "(" + str(coordX) + "," + str(coordY) + ")"
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%m/%d/%Y %H:%M:%S')
    string = 'Time: ' + str(st) + " Axis: " + ax + ' Coordinates: ' + crd + ' \n'
    for i in data.split():
        string = string + str(i) + '\n'
    string = string + "######################################\n"
    master_raw.write(string)

start_time = datetime.now()

# Probe with statement begins
with serial.Serial(port='COM3', baudrate=115200, timeout=1) as probe:  # # # Opening serial connection w/ probe.
    # Probe initialization
    print("Connection to probe successful. Begin auto start.")  # Note: Probe accepts only one connection at a time
    flush()  # Clears out the serial buffer. It is uncertain whether this step is necessary.
    # Autostart Mode
    probe.write(str.encode(">"))  # Tells sensors to enter Autostart Mode.
    autocheck(1)                # Makes sure autostart executed succesfully
    probe.write(str.encode("B"))  # Writes to sensor: Dual Axis Mode      ---------- contingent on axis mode?
    print("Begin Field Zero:")
    probe.write(str.encode("D"))  # Field Zero ON Command
    time.sleep(20)
    flush()
    time.sleep(5)
    num = probe.in_waiting  # This block reads the buffer. Num is the number of bits waiting in the buffer.
    buffer = probe.readlines(num)  # Loads the buffer into a variable as a list of strings
    flush()
    zeroField = zeroExtract(buffer)
    print("Field zero finished. Final zero field values:")
    print(zeroField)
    print("Beginning calibration.")
    probe.write(str.encode("9"))  # "Calibrate"
    time.sleep(5)
    print("Calibration finished.")
    probe.write(str.encode("7"))  # Print ON Command
    time.sleep(10)
    flush()

# Command Parsing Begins

    print("Command parsing begins.")
    for line in commands.split("\n"):
        if line == "Zero X Axis":
            ZeroX()
        elif line == "Zero Y Axis":
            ZeroY()
        elif line == "Take Field Measurement":
            Measure()
        else:  # this awkward 'else' statement is meant to take care of both move functions and
            com = line.split(" ")  # straggling empty lines that may appear in the pre-image
            if len(com) > 5:
                if com[0] == "Move" and com[5] == "X":
                    MoveX(int(com[1]))
                elif com[0] == "Move" and com[5] == "Y":
                    MoveY(int(com[1]))
            else:
                pass

    print("Command parsing over.")
    flush()
    probe.write(str.encode("8"))            # Probe Print OFF

# Probe with statement ends. At this point it's okay to turn off the probe

# now we iterate through the raw data file and process measurements
for package in ((master_raw.read()).split("######################################")):
    rlines = package.split("\n")
    rhead = rlines[0].split(" ")
    rts = rhead[1] + " " + rhead[2]     # timestamp, axis, coordinate gathered for later
    rax = rhead[4]
    rcoord = rhead[6]
    rest = rlines[1:]
    picovals = []
    for line in rest:
        if (len(line) == 8) and (line[0] == "!"):
            picovals = picovals + [fieldReading(line)]
        else:
            pass
    # First order statistics ; averaging of raw values etc.
    rave = round((stat.mean(picovals)), 2)      # average picotesla value and standard deviation collected
    rstd = round((stat.pstdev(picovals)), 2)
    mline = rts + "\t" + rcoord + "\t\t" + rax + "\t" + rave + "\t\t" + rstd + "\n"
    master_data.write(mline)

# this creates a matrix of mag field measurement values where matrix index corresponds to plate-space
if samplingPattern == "simple":
    resx = int(resolution.split("x")[0])
    resy = int(resolution.split("x")[1])
    posgrid = []
    for i in range(resx + 1):           # construction of array with dummy values of appropriate dimensions
        posgrid = posgrid + [[]]
        for j in range(resy + 1):
            posgrid[i] = posgrid[i] + [['y','z']]
    for line in master_data:
        spline = line.split("\t")
        coord = spline[1]
        xcoo = coord.split(",")[1:]
        ycoo = coord.split(",")[:-1]
        ax = spline[2]
        if ax == "Y":
            ax = 0
        else:
            ax = 1
        picot = spline[3]
        standev = spline[4]
        (((posgrid[ycoo])[xcoo])[ax]) = [picot, standev]

# this if statement splits the data into individual line files
if scheme == "x-linear":
    for y in range(len(posgrid)):
        for x in range(len(posgrid[0])):
            pos = "(" + x + "," + y + ")"
            point = (posgrid[y])[x]
            yMag = point[0][0]
            yStd = point[0][1]
            zMag = point[1][0]
            zStd = point[1][1]
            line = pos + "\t" + str(yMag) + "\t\t" + str(yStd) + "\t\t" + str(zMag) + "\t\t" + str(zStd) + "\n"
            line_dict[y].write(line)