# Motor Functions
#
#
# Notes:
#   - The plate dimensions and resolution are going to have to be set to this in order to get a 3mmx3mm cell size:
#       plateDimensions = "67x511"       # in format "NxM" where units are in centimeters and N,M floats
#       resolution = "23x171"              # in format "LxP" where L and P of integer value;
#
#   - There are some print commands that are commented that you may want to take out
#   - make sure the axis mode for the Geneva gear is initally stated somewhere as "xy"
#   - These are the global commands I'm using here, which may need to be translated:
#       axisMode  ---  state of the geneva gear axis. Either "xy" or "yz"
#       xlen
#       ylen   ------  see the comment in the third lines of both the MoveX() and MoveY() functions. also see lines 48-49.
#                      xlen and ylen should be in mm.
#       probeX
#       probeY   ----  defined coordinates of X and Y. 
#
#              ***** IMPORTANT ***** -- in the pre-map code, xCell and yCell (which, I believe, are our xlen and ylen equivalents) 
#                                       need to be rounded floats. See below for corrected versions, written as variables xlen and 
#                                       ylen on lines 48-49.
###############################################################################################################################################

# Things that need to be initialized:

import serial
import time

motor = serial.Serial('COM1')           #initializes the serial port for the motors
motor.write(str.encode('DRIVE1011:'))   #enables the motor drives

motion_profile = ("MA 0X00:",                               #creates the motion profile list that will be sent to the motors
                  "A 35,,50,50:",
                  "AA 17.500000,,25.000000,25.000000:",
                  "AD 35,,50,50:",
                  "ADA 17.500000,,25.000000,25.000000:",
                  "V 3.5,,5,5:",
                  "",                                       #this item in the list defines the distance the motor travels, will be filled in later
                  "MC 0X00:")
motion_profile=list(motion_profile)

probeX = 0
probeY = 0

plateDimensions = "67x511"       # in format "NxM" where units are in centimeters and N,M floats. Units = mm
resolution = "23x171"              # in format "LxP" where L and P of integer value; Units = "chunks", "cells", whatever you wanna call it

xlen = round(float((plateDimensions.split("x"))[0]) / float((resolution.split("x"))[0]),6)
ylen = round(float((plateDimensions.split("x"))[1]) / float((resolution.split("x"))[1]),6)      # xlen and ylen are the physical dimensions
                                                                                                # in mm of a resolution-square (or pixel)

######################## Function definitions:


def moveMotors(dist1000, dist0010, dist0001):
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 1011:"))


def RotateTo(axisGoTo):  #Geneva gear axis rotation command. Expects input of the state you want to go to. Initializes in "xy" state.
                         #  If it's in "xy" state and is told to move to "xy", will pass. If told to move to "yz", will move.
                         #  Likewise, if it's told to move to "yz" and it's already in "yz", won't move. Will move only to "xy".
    global axisMode
    if axisMode == "xy":
        if axisGoTo == "xy":
            pass
        elif axisGoTo == "yz":
            moveMotors(8192,0,0)
            cooldown(8192,1)
            axisMode = "yz"
    elif axisMode == "yz":
        if axisGoTo == "yz":
            pass
        elif axisGoTo == "xy":
            moveMotors(-8192,0,0)
            cooldown(8192,1)
            axisMode = "xy"

def MoveX(s):
    global probeX
    global xlen         # <-- or whatever equivalent variable that will be defined for the total map length divided by the resolution
    distX = s * xlen * (4096/2) # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    distX = int(round(distX,0))
    if s < 0:
        distX = distX - 4000
        moveMotors(0,distX,0)
        cooldown(distX, 3)
        distX = 4000
        moveMotors(0,distX,0)
        cooldown(distX,3)
    elif s > 0:
        moveMotors(0,distX,0)
        cooldown(distX,3)
    probeX = probeX + s


def MoveY(s):
    global probeY
    global ylen         # <-- or whatever equivalent variable that will be defined for the total map length divided by the resolution
    distY = s * ylen * (4096/2) # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    distY = int(round(distY,0))
    if s < 0:
        distY = distY - 4000
        moveMotors(0,0,distY)
        cooldown(distY,4)
        distY = 4000
        moveMotors(0,0,distY)
        cooldown(distY,4)
    elif s > 0:
        moveMotors(0,0,distY)
        cooldown(distY,4)
    probeY = probeY + s

####will send a MoveXY command later on 

def HomeX():
    #print("Moving to X home position...")
    global probeX
    motion_profile[5] = "V 3.5,,2,2:"
    moveMotors(0,-300000,0)                 #moves this distance back in order to hit negative limit switch
    cooldown(-300000,3)

    moveMotors(0,6000,0)                    #moves forward ~2mm to beginning test position
    cooldown(6000,3)

    probeX = 0
    motion_profile[5] = "V 3.5,,5,5:"       #resets the motion profile to the previous 5 rotations/second for Axis 3, Axis 4
    #print("X homing complete.")


def HomeY():
    #print("Moving to Y home position...")
    global probeY
    motion_profile[5] = "V 3.5,,2,2:"
    moveMotors(0,0,-1000000)                #moves this distance back in order to hit negative limit switch
    cooldown(-1000000,4)

    moveMotors(0,0,6000)                    #moves forward ~2mm to beginning test position
    cooldown(6000,4)

    probeY = 0
    motion_profile[5] = "V 3.5,,5,5:"       #resets the motion profile to the previous 5 rotations/second for Axis 3, Axis 4
    #print("Y homing complete.")


def ZeroX():
    global probeX
    if probeX > 0:
        MoveX(-1 * probeX)

def ZeroY():
    global probeY
    if probeY > 0:
        MoveY(-1 * probeY)


def cooldown(distSteps, waitAxis):        #defines a function that can calculate wait time between executing moves. Expects length of travel in motor steps (1rev=4096 steps) and axis                   
    distSteps = abs(distSteps)
    vel = motion_profile[5]
    print(vel)
    if waitAxis == 3:
        rps = vel[7]                        #this variable grabs the x rotations per second from the motion profile 
    elif waitAxis == 4:
        rps = vel[9]                        #same as above, except y
    elif waitAxis == 1:
        rps = 3                             #same as above, except for Geneva gear axis
    rot = distSteps/4096                   #rot is total rotations that need to be executed by the motor to go the distance distSteps
    waitTime = float(rot)/float(rps)     #total rotations over rotations per second gives the (approximate) time it'll take the motors to move
    waitTime = waitTime + 1
    if distSteps > (250*2048):
        waitTime = waitTime + 1.5
    waitTime = round(waitTime,3)
    #print("Waiting " + str(waitTime) + " seconds for motors to move...")
    time.sleep(waitTime)
    #print("done")



