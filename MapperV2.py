#MapperV1.py


#**NOTES** (comments section, things to be addressed while integrating code):
	#C: xlen needs to be in mm
	#A: will have to figure out 2 serial ports
	#B: do the variables from the header of the preImage file need to be global?
	#D: get the updated version of Pre-Imaging-Test.py to see how X Cell Length and Y Cell Length are calculated
	#E: I still don't understand os.path() and os.mkdir. Ask Lukas
	#F: Does this command create the file or just open it? Related to Note E
	#G: need to fix coil values. For initial test maps using fake plates, I think we should include the coordinates of the dipole--
		#but this is just for the sake of keeping a record, and should be more simple than a whole fake dipole in the data
	#H: would like to create an estimated time for the map, but this will require more time to think about and isn't an immediate concern
	#I: where to put start_time = datetime.now() ?
	#J: not sure if I need to establish this as a global variable if it gets directly inputted into the function. Don't think I do

	#Additional Notes:
	#learn how to insert prompts when user runs code
		#create an option to prompt user for plate number upon running code, and put this into the title of the map or the Info file
		#also maybe prompt for the location of the preImage file using a dialog window
		#or actually, create these prompts in the preImage code, because then that file can just be selected and will correspond to a specific plate
			#Make a GUI
	#Change all "preImage" to "preMap"? Makes more sense
	#Call upon functions in Dual-Axis-Test.py to save data

######################################################################################
#Importing appropriate directories and establishing global variables

import serial
import math
import os.path
from datetime import datetime
from datetime import timedelta

# 'Hardcoded' Values

probeH = 1            									# Probe height from plate in cm
xOn = True           									# Set to true / false to activate measurement in this axis
yOn = True
zOn = True

# Suppose a dummy coil at position (x,y) on the plate of variable radius, amperage, etc.

coilRadius = 1         									# Radius of coil embedded in fake plate, in mm
coilAmps = .1
coilPosition = "(x,y)" 									#"center" for center of plate, "random" for pseudorandom positioning, "(x,y)" for specific gridwise location

coilMag = coilAmps * math.pi * (coilRadius * 0.01)**2 	#magnetization of the dipole (from Griffiths)
mag = [0,0,coilMag]

#Parameters for Map Information

mapTitle = "default"    						#leave "default" for default map naming scheme
operatorComments = ""   						#leave your comments here


#Parameters for the Motors

ser=serial.Serial('COM1')						#initializes the serial port for the motors  **SEE NOTES A**
ser.write(str.encode('DRIVE0011:'))				#enables x and y axis motors

motion_profile = ("MA XX00:",					#creates the motion profile list that will be sent to the motors
"A ,,10,10:",
"AA ,,5.000000,5.000000:",
"AD ,,10,10:",
"ADA ,,5.000000,5.000000:",
"V ,,4,3:",
"",												#this item in the list defines the distance the motor travels, will be filled in later
"MC XX00:")
motion_profile=list(motion_profile)

dist0010 										#establishes variables that will be eventually inserted into motion profile
dist0001
#s 												#establishes global variable for steps; see comment in moveX function

plateDim										#initializes relevant variables from header **SEE NOTES B**
resolution
samplingPattern
scheme
xlen 											
ylen

####################################################################################
#Definitions of functions to be used in the code


def MoveX(s):									#expects s (steps)
	global dist0010
	global dist0001 
	global xlen
	#global s 									#**SEE NOTES J**
	dist0010 = s * xlen * 4096/2				#each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
	dist0001 = 0
	motion_profile[6]= "D ,,"+str(dist0010)+","+str(dist0001)+":"
	for command in motion_profile:
		ser.write(str.encode(command))
	ser.write(str.encode("GO 0010:"))

def MoveY(s):									#expects s (steps)
	global dist0010
	global dist0001 
	global ylen
	#global s 									#**SEE NOTES J**
	dist0010 = 0				
	dist0001 = s * ylen * 4096/2 				#each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
	motion_profile[6]= "D ,,"+str(dist0010)+","+str(dist0001)+":"
	for command in motion_profile:
		ser.write(str.encode(command))
	ser.write(str.encode("GO 0001:"))

#This is here in case we want to move both motors at the same time
def MoveXY(sX,sY):								#expects sX and sY inputs (steps to move in x and y direction, respectively)
	global dist0010
	global dist0001 
	global xlen
	global ylen
	#global s 									#**SEE NOTES J**
	dist0010 = sX * xlen * 4096/2	
	dist0001 = sY * ylen * 4096/2 	
	motion_profile[6]= "D ,,"+str(dist0010)+","+str(dist0001)+":"
	for command in motion_profile:
		ser.write(str.encode(command))
	ser.write(str.encode("GO 0011:"))

#Not entirely sure how to do these two yet, I'll have to go to CEEM to see how the limit switches perform
def HomeX():

def HomeY():

def ZeroX():

def ZeroY():

def Measure():

####################################################################################
####################################################################################
####################################################################################
#Initialization of code. First section calls upon preImage file to extract info. 

preImageFilename = "simple_50x50_05.22.2020_16.38.56.txt"							#name of preImage file from which to draw commands/info in order to execute the map
preImageLocation = "C:/Users/lsead/Desktop/CEEM Remote/MapPlanner/TestFolder"		#name of preImage folder from which to draw the preImage file
dataDestination = "C:/Users/lsead/Desktop/CEEM Remote/MapPlanner/TestFolder"		#what folder to write the data file to
preImage = (open(os.path.join(preImageLocation, preImageFilename),"r")).read()

header = preImage.split("###############################")[0]						#splits the preImage file into two relevant lists; header and commands
commands = preImage.split("###############################")[1]

for line in header.split("\n"):            			    							#initializes relevant variables from header **SEE NOTES B**
    if line[:17] == "Plate Dimensions:":											#reads header line-by-line and extracts values of variables that depend on pre-image input parameters
        global plateDim 
        plateDim = line[18:-4]
    elif line[:15] == "Map Resolution:":
        global resolution
        resolution = line[-5:]
    elif line[:17] == "Sampling Pattern:":
        global samplingPattern
        samplingPattern = line[18:]
    elif line[:12] == "Data Scheme:":
        global scheme
        scheme = line[13:]
    elif line[:14] == "X Cell Length:":
        global xlen
        xlen = float(line[15:-3]) * 0.01											#xlen and ylen are the distance in centimeters of a resolution 'step' in each respective direction, in mm **SEE NOTES D**
    elif line[:14] == "Y Cell Length:":
        global ylen
        ylen = float(line[15:-3]) * 0.01											

date_time = (datetime.now()).strftime("%m.%d.%Y_%H.%M.%S")							#establishes the start time of the map


if mapTitle == "default":
    mapTitle = samplingPattern + "_" + resolution + "_" + date_time + "_MAP"

finalDest = os.path.join(dataDestination, mapTitle)									#**SEE NOTES E**
os.mkdir(finalDest)


#Initialization of Data Files. Next part 

info_file = open(os.path.join(finalDest, "info.txt"), "w+")         				#a file containing information on the mapping run **SEE NOTES F**
master_data = open(os.path.join(finalDest, "master.txt"), "w+")     				#time series that will contain everything, for good measure
master_head = "Timestamp:\t\tPosition:\t\tXfield:\t\t\tYfield:\t\t\tZfield\n"		#writes a header for the master file, right off the bat
master_data.write(master_head)

if scheme == "x-linear":                                							#creates a text file for each line of measurements by the y-axis
    global line_dict
    line_dict = []
    for i in range(1 + int((resolution.split("x"))[1])):
        line_dict = line_dict + [open(os.path.join(finalDest, ("line" + str(i) + ".txt")), "w+")]
        line_dict[i].write(master_head)

###################################################################################
#This part of the code is actually reading the file and executing the commands
	#by calling the functions above.

for line in commands.split("\n"):
    if line == "Zero X Axis":
        ZeroX()
        
    elif line == "Zero Y Axis":
        ZeroY()
    elif line == "Take Field Measurement":
        Measure()
    else:
        com = line.split(" ")
        if len(com) > 5:                                #if line has more than 5 words (avoids blank line error)
            if com[0] == "Move" and com[5] == "X":
                global s                                #calls global variable s and sets it equal to # of steps it has to move
                s = int(com[1]) 						#might actually change this so s is local and not global
                MoveX(int(com[1]))
            elif com[0] == "Move" and com[5] == "Y":
                global s 
                s = int(com[1])
                MoveY(s,ylen)
        else:
            pass

###################################################################################
#Final part of code populates all the information for the Info file. This is last b/c it should include the time it took for the map to complete.

info1 = "Map Parameters.\n\n"
axes = ""

if xOn:
    axes = axes + "X "
if yOn:
    axes = axes + "Y "
if zOn:
    axes = axes + "Z "

hardcodedvals = "Probe Height: " + str(probeH) + "cm\nMeasurement Axes: " + axes + "\n"
#coilCoord = ("(" + str(int(round(dipX / xlen, 0))) + "," + str(int(round(dipY / ylen, 0))) + ")")		#**SEE NOTES G**
#coilvals = "Coil Radius: " + str(coilRadius) + " cm\nCoil Current : " + str(coilAmps) + "amps\n" + "Coil Coordinates: " + coilCoord + "\n"

#info_file.write(info1 + hardcodedvals + coilvals)														#**SEE NOTES G**


info_file.write("Map Started: " + start_time.strftime("%m/%d/%Y_%H:%M:%S") + "\nMap Finished: "  + (start_time + timedelta(seconds=time)).strftime("%m/%d/%Y %H:%M:%S"))
																										#**SEE NOTES I**
#info_file.write("\nEstimated Map Time: " + str(time)[:8] + " seconds\n")								#**SEE NOTES H**

info_file.write("\nComments:\n" + operatorComments + "\n")

info_file.write("\nHeader from Image File:\n" + header)
