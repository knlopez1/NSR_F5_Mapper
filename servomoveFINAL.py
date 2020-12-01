import serial
import time
ser=serial.Serial('COM1')					#initializes the serial port for the motors
ser.write(str.encode('DRIVE1011:'))			#enables the drives


motion_profile = ("MA 0X00:",				#creates the motion profile list that will be sent to the motors
"A 35,,50,50:",
"AA 17.500000,,25.000000,25.000000:",
"AD 35,,50,50:",
"ADA 17.500000,,25.000000,25.000000:",
"V 3.5,,5,5:",
"",											#this item in the list defines the distance the motor travels, will be filled in later
"MC 0X00:")
motion_profile=list(motion_profile)

# def tune_servos():
# 	SGP 2,0.5,3,1.6
# 	SGI 3,0,3.5,1.6
# 	SGILIM 0,0,0,0
# 	SGV 4,0,2.5,2
# 	SGVF 0,0,0,0
# 	SGAF 0,0,0,0

def move_servos(d1,d3,d4):		#expects distance values for each axis in steps --> 4096 steps = 1 rev = 2 mm

	global dist1000
	global dist0010
	global dist0001
	dist1000 = d1
	dist0010 = d3
	dist0001 = d4
	
	motion_profile[6]= "D "+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"	#writes the distances into the motion profile list
	for command in motion_profile:													#writes each item in motion profile to the motors
		ser.write(str.encode(command))
	ser.write(str.encode("GO 1011:"))												#tells motors to go

move_servos(0,0,0)