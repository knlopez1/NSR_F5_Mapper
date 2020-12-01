

#Notes:
    #cooldown function
    #fix axes to be 0,1,2 options 
    #need an initialization function to get motors to limit switches (ZeroX and ZeroY won't work if probeX and probeY are initialized at 0)
#############################################################################################################################

#This code is for a test to see how much drift the Velmex translation stages accumulate over repeated back-and-forth motion 
#   (to see if the motors end up where they *think* they end up).
#
#Qualitative Test Description (1 axis):
#   The motors will zero to a "home" position defined by the end-of-travel limit switch. Then they will back away to a set distance from the switch**
#   and set the coordinate variables probeX and probeY to zero. Then, it will prompt the user to input a starting x-hat distance. This should be measured
#   with a caliper from the inner wall of the Velmex linear translation stage frame to the side of the translation stage itself. Next, the motors will move
#   s steps away from the limit switch, followed by s steps back. This is considered one rep. This motion will be executed however many times the variable 
#   'reps' is set to. When this is finished, the system will prompt the user again to input a final x-hat distance, which should be measured as closely as
#   possible (procedurally speaking) to the starting x-hat position. Then, the program will print all values including errors. 
#
#   For now, we run this test assuming use of the *positive* end-of-travel limit switch. It will need to be modified to be run using the negative limit
#   switch to see if there is any difference in drift between the near and far ends of the travel relative to the motor. 
#
#
#   **Upon initial zeroing when the motors back away to a set distance from the limit switch, they will back away and intentionally overshoot by a set amount, followed by a
#     re-backing up in the direction of the switch to the correct distance. That way the direction of approach is *towards* the limit switch, which is the same direction of
#     approach that the motors will end the test on when finishing the back-and-forth reps. This eliminates any possible error due to play in the lead screw of the stage.
#
#
#Homing procedure:
#   In order to minimize hitting the limit switch at full speed during initial homing, the motion profile will be set to 1 rev/s and the motor will be prompted to travel
#   the full length of travel plus a small amount so that regardless of where the stage starts, it will hit the limit switch. Because there is no feedback via python of
#   how far the stage had to travel before hitting the switch, a wait command will be implemented that assumes the stage is as far as possible and must execute the full
#   length of travel (even if in reality this is not the case). This will lead to some intentional dead time at the beginning of the test, but no more than 4 or 5 minutes. 
#   Otherwise, Python would not wait until the switch was hit before sending the next command. 
#
#
#############################################################################################################################
import serial
import time

# 'Hardcoded' Values

probeVel = .25          #in meters per second
xlen = 60                #xlen (in mm) is the distance per "step" as the motor travels in a direction for 's' number of steps
ylen = 60
cooldown = 9

# User Variables

reps = 10                              #number of 'reps'     ---    estimate a test to take 3 seconds per rep
#rotDistance = 50
axes = [True, False, False]               #[X-hat, Y-hat, Dual-Axis]

# Motor Initialization

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

# Motor Movement Functions

global probeX
global probeY

probeX = 0      #probe X variable is the coordinate in steps 's' (1 step = xlen (mm)). Initially set to 0.
probeY = 0

def MoveX(s):  # expects s (steps)
    global probeX
    global xlen
    dist1000 = 0
    dist0010 = s * xlen * (4096 / 2)    # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    dist0001 = 0
    motion_profile[6] = "D" + str(dist1000) + ",," + str(dist0010) + "," + str(dist0001) + ":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    time.sleep(cooldown)
    probeX = probeX + s
    print("Current x-coordinate: " + str(probeX))

def MoveY(s):  # expects s (steps)
    global probeY
    global ylen
    dist1000 = 0
    dist0010 = 0
    dist0001 = s * ylen * 4096 / 2      # each rotation of translation stage is 4096 "steps" of motor, and travels 2mm
    motion_profile[6] = "D" + str(dist1000) + ",," + str(dist0010) + "," + str(dist0001) + ":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    time.sleep(cooldown)
    probeY = probeY + s
    print("Current y-coordinate: " + str(probeY))


def MoveXY(sX, sY):  # expects sX and sY inputs (steps to move in x and y direction, respectively)
    global probeX
    global probeY
    global xlen
    global ylen
    dist1000 = 0
    dist0010 = sX * xlen * 4096 / 2
    dist0001 = sY * ylen * 4096 / 2
    motion_profile[6] = "D" + str(dist1000) + ",," + str(dist0010) + "," + str(dist0001) + ":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0011:"))
    time.sleep(cooldown)
    probeX = probeX + sX
    probeY = probeY + sY
    print("Current x-coordinate: " + str(probeX))
    print("Current y-coordinate: " + str(probeY))

# implementation of 'naive' non-homing zeroing procedures

def ZeroX():
    global probeX
    if probeX == 0:
        pass
    else:
        MoveX(-1 * probeX - 10)             # Nominally moves ten steps past zero on x-axis
        probeX = 0

def ZeroY():
    global probeY
    if probeY == 0:
        pass
    else:
        MoveY(-1 * probeY - 10)
        probeY = 0

def HomeX():
    global probeX
    global probeY
    dist1000 = 0
    dist0010 = 300000                      #moves this distance forward in order to hit positive limit switch
    dist0001 = 0
    motion_profile[5] = "V 3.5,,2,2:"
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    time.sleep(20)

    dist0010 = -15000                       #backs off the limit switch ~7mm
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    time.sleep(10)

    dist0010 = 5000                         #returns back in the direction of the limit switch ~2mm to beginning test position
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0010:"))
    time.sleep(3)

    probeX = 0
    motion_profile[5] = "V 3.5,,5,5:"                   #resets the motion profile to the previous 5 rotations/second for Axis 3, Axis 4

def HomeY():
    global probeX
    global probeY
    dist1000 = 0
    dist0010 = 0                      
    dist0001 = 1000000                  #moves this distance forward in order to hit positive limit switch
    motion_profile[5] = "V 3.5,,2,2:"
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    time.sleep(120)

    dist0001 = -15000                       #backs off the limit switch ~7mm
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    time.sleep(10)

    dist0001 = 5000                         #returns back in the direction of the limit switch ~2mm to beginning test position
    motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
    for command in motion_profile:
        motor.write(str.encode(command))
    motor.write(str.encode("GO 0001:"))
    time.sleep(3)

    probeY = 0
    motion_profile[5] = "V 3.5,,5,5:"                   #resets the motion profile to the previous 5 rotations/second for Axis 3, Axis 4


def cooldown():
    global probeX
    global probeY
    vel = motion_profile[5]
    


#############################################################################################################################
# X-hat Test

if axes[0]:

    print("Testing testing 123")
    time.sleep(3)
    HomeX()
    #HomeY()

    xstartVal = float(input("Input starting x-hat distance: "))
    print("Your input: " + str(xstartVal))

    # Reps begin.

    for i in range(reps):
        MoveX(-1)
        MoveX(1)

    xendVal = float(input("Input final x-hat distance: "))
    print("Your input: " + str(xendVal))

    xerror = xendVal - xstartVal

    xmessage = "Initial value: " + str(xstartVal) + "\nFinal value: " + str(xendVal) + "\nTotal error: " + str(xerror) + "\n" + "Error per rep: " + str(xerror / reps)
    print(xmessage)

# Y-hat Test

# if axes[1]:

#     # Move probe to (50mm,0) then to (50mm,10mm)

#     ZeroX()
#     ZeroY()
#     MoveX(50)
#     MoveY(10)

#     ystartVal = float(input("Starting y-hat distance?"))
#     print("You input:" + str(ystartVal))

#     # y-reps

#     for i in range(reps):
#         MoveY(50)
#         MoveY(-50)

#     yendVal = float(input("Final y-hat distance?"))
#     print("You input:" + str(yendVal))

#     yerror = yendVal - ystartVal

#     ymessage = "Initial value: " + str(ystartVal) + "\nFinal value: " + str(yendVal) + "\nTotal error: " + \
#                str(yerror) + "\nError per rep: " + str(yerror / reps)
#     print(ymessage)


# # Dual-Axis Test

# if axes[2]:

#     # Move probe to (10mm,10mm)

#     ZeroX()
#     ZeroY()
#     MoveXY(10,10)

#     xstartVal = float(input("Starting x-hat distance?"))
#     ystartVal = float(input("Starting y-hat distance?"))
#     print("Your x input:" + str(xstartVal))
#     print("Your y input:" + str(ystartVal))

#     for i in range(reps):
#         MoveXY(25,25)
#         MoveXY(-25,-25)
#         # move probe back and forth

#     xendVal = float(input("Final x-hat distance?"))
#     yendVal = float(input("Final y-hat distance?"))
#     print("Your x input:" + str(xendVal))
#     print("Your y input:" + str(yendVal))

#     xerror = xendVal - xstartVal
#     yerror = yendVal - ystartVal

#     xmessage = "Initial value: " + str(xstartVal) + "\nFinal value: " + str(xendVal) + "\nTotal error: " + \
#                str(xerror) + "\nError per rep: " + str(xerror / reps)
#     ymessage = "Initial value: " + str(ystartVal) + "\nFinal value: " + str(yendVal) + "\nTotal error: " + \
#                str(yerror) + "\nError per rep: " + str(yerror / reps)
#     print("X-axis:\n" + xmessage + "\nY-axis:\n" + ymessage)

#ZeroX()
#ZeroY()
