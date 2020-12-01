import serial
ser=serial.Serial('COM1')
#enabledrive
ser.write(str.encode('DRIVE0011:'))

#Motion Profile
motion_profile = ("MA XX00:",
"A ,,,10:",
"AA ,,,5.000000:",
"AD ,,,10:",
"ADA ,,,5.000000:",
"V ,,,3:",
"",
"MC XX00:")
motion_profile=list(motion_profile)

def move_servos(d3,d4):

	global dist0010
	global dist0001
	dist0010= d3
	dist0001= d4
	#Read motion profile
	motion_profile[6]= "D ,,"+str(dist0010)+","+str(dist0001)+":"
	for command in motion_profile:
		ser.write(str.encode(command))
	ser.write(str.encode("GO 0011:"))

#move_servos(4096,0)
move_servos(0,-8192)