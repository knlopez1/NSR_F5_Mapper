# Motor Functions
#
#
# Notes:
#   - The plate dimensions and resolution are going to have to be set to this in order to get a 3mmx3mm cell size:
#       plateDimensions = "67x511"       # in format "NxM" where units are in centimeters and N,M floats
#       resolution = "23x171"              # in format "LxP" where L and P of integer value;
#
#   - There are some print commands that are commented that you may want to take out
#   - Pick whichever ZeroX and ZeroY commands you like more. I don't know if an else statement is necessary
#   - make sure the axis mode for the Geneva gear is initally stated somewhere as "xy"
#   - These are the global commands I'm using here, which may need to be translated:
#       axisMode  ---  state of the geneva gear axis. Either "xy" or "yz"
#       xlen
#       ylen   ------  see the comment in the third lines of both the MoveX() and MoveY() functions.
#                      xlen and ylen should be in mm.
#       probeX
#       probeY   ----  defined coordinates of X and Y. 
#
#              ***** IMPORTANT ***** -- in the pre-map code, xCell and yCell (which, I believe, are our xlen and ylen equivalents) 
#                                       need to be floats. I have more questions about this for when we actually meet.
###############################################################################################################################################

def RotateTo(axisGoTo):  #Geneva gear axis rotation command. Expects input of the state you want to go to. Initializes in "xy" state.
                         #  If it's in "xy" state and is told to move to "xy", will pass. If told to move to "yz", will move.
                         #  Likewise, if it's told to move to "yz" and it's already in "yz", won't move. Will move only to "xy".
    global axisMode
    if axisMode == "xy":
        if axisGoTo == "xy":
            pass
        elif axisGoTo == "yz":
            dist1000 = 4096 * 2
            dist0010 = 0
            dist0001 = 0
            motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
            for command in motion_profile:
                motor.write(str.encode(command))
            motor.write(str.encode("GO 1000:"))
            cooldown(dist1000,1)
            axisMode = "yz"
    elif axisMode == "yz":
        if axisGoTo == "yz":
            pass
        elif axisGoTo == "xy":
            dist1000 = -1 * 4096 * 2
            dist0010 = 0
            dist0001 = 0
            motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
            for command in motion_profile:
                motor.write(str.encode(command))
            motor.write(str.encode("GO 1000:"))
            cooldown(dist1000,1)
            axisMode = "xy"


def MoveX(s):  # expects s (steps)
    global probeX
    global xlen         # <-- or whatever equivalent variable that will be defined for the total map length divided by the resolution
    dist1000 = 0
    dist0010 = s * xlen * (4096 / 2)    # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    dist0001 = 0
    if s < 0:
        dist0010 = dist0010 - 3000
        motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in motion_profile:
            motor.write(str.encode(command))
        motor.write(str.encode("GO 0010:"))
        cooldown(dist0010,3)
        dist0010 = 3000
        motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in motion_profile:
            motor.write(str.encode(command))
        motor.write(str.encode("GO 0010:"))
        time.sleep(1)
    elif s > 0:
        motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in motion_profile:
            motor.write(str.encode(command))
        motor.write(str.encode("GO 0010:"))
        cooldown(dist0010,3)
    probeX = probeX + s
    #print("Current x-coordinate: " + str(probeX))


def MoveY(s):  # expects s (steps)
    global probeY
    global ylen         # <-- or whatever equivalent variable that will be defined for the total map length divided by the resolution
    dist1000 = 0
    dist0010 = 0
    dist0001 = s * ylen * (4096 / 2)    # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    if s < 0:
        dist0001 = dist0001 - 3000
        motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in motion_profile:
            motor.write(str.encode(command))
        motor.write(str.encode("GO 0001:"))
        cooldown(dist0001,4)
        dist0001 = 3000
        motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in motion_profile:
            motor.write(str.encode(command))
        motor.write(str.encode("GO 0001:"))
        time.sleep(1)
    elif s > 0:
        motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in motion_profile:
            motor.write(str.encode(command))
        motor.write(str.encode("GO 0001:"))
        cooldown(dist0001,4)
    probeY = probeY + s
    #print("Current x-coordinate: " + str(probeX))


####will send a MoveXY command later on 


def HomeX():
    #print("Moving to X home position...")
    global probeX
    dist1000 = 0
    dist0010 = -300000                      #moves this distance backward in order to hit negative limit switch
    dist0001 = 0
    motion_profile[5] = "V 3.5,,2,2:"
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    time.sleep(20)

    dist0010 = 5000                         #moves forward ~2mm to beginning test position
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    time.sleep(2)

    probeX = 0
    motion_profile[5] = "V 3.5,,5,5:"       #resets the motion profile to the previous 5 rotations/second for Axis 3, Axis 4
    #print("X homing complete.")


def HomeY():
    #print("Moving to Y home position...")
    global probeY
    dist1000 = 0
    dist0010 = 0                      
    dist0001 = -1000000                      #moves this distance backward in order to hit negative limit switch
    motion_profile[5] = "V 3.5,,2,2:"
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    time.sleep(123)

    dist0001 = 5000                         #moves forward ~2mm to beginning test position
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    time.sleep(2)

    probeY = 0
    motion_profile[5] = "V 3.5,,5,5:"       #resets the motion profile to the previous 5 rotations/second for Axis 3, Axis 4
    #print("Y homing complete.")


def ZeroX():
    global probeX
    if probeX == 0:
        pass
    else:
        MoveX(-1 * probeX)

def ZeroY():
    global probeY
    if probeY == 0:
        pass
    else:
        MoveX(-1 * probeY)


###Alternatively:###
def ZeroX():
    global probeX
    if probeX > 0:
        MoveX(-1 * probeX)

def ZeroY():
    global probeY
    if probeY > 0:
        MoveY(-1 * probeY)
####################


def cooldown(distSteps, waitAxis):        #defines a function that can calculate wait time between executing moves. Expects length of travel in motor steps (1rev=4096 steps) and axis                   
    vel = motion_profile[5]
    if waitAxis == 3:
        rps = vel[7]                        #this variable grabs the x rotations per second from the motion profile 
    elif waitAxis == 4:
        rps = vel[9]                        #same as above, except y
    elif waitAxis == 1:
        rps = 3                             #same as above, except for Geneva gear axis
    rot = distSteps/4096                   #rot is total rotations that need to be executed by the motor to go the distance distSteps
    waitTime = float(rot)/float(rps)     #total rotations over rotations per second gives the (approximate) time it'll take the motors to move
    waitTime = waitTime + 1
    #print("Waiting " + str(waitTime) + " seconds for motors to move...")
    time.sleep(waitTime)







