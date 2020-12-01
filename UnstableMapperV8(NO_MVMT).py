from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
import webbrowser
import os
import time
from datetime import datetime
import serial
import statistics as stat
import threading


class timerSignals(QObject):
    """
    Defines signals available to timer background process.

        message
            'string'
    """
    message = pyqtSignal(str)


class mappingSignals(QObject):
    """
    Defines signals available to main mapping process.

        moveUpdate
            'tuple' (Next Point)

        measureUpdate
            'tuple' (Measured Point)

        message
            'string'

        criticalError
            'string'

        commandDone
            No Data

        mapFinished
            No Data
    """
    moveUpdate = pyqtSignal(list)  # Tells GUI which points have been mapped for visualization
    measureUpdate = pyqtSignal(list)
    message = pyqtSignal(str)  # Passes messages to internal GUI comms
    criticalError = pyqtSignal(str)  # Passes messages to internal GUI comms, kills process, spits out error report
    commandDone = pyqtSignal()  # Tells GUI that current command has been processed
    mapFinished = pyqtSignal()  # Tells GUI that the map is finished.



#################################################################################################################
######################################     MAIN CLASS     #######################################################
#################################################################################################################



# Thread object for main mapping process:
class mappingProcess(QRunnable):
    def __init__(self, args):
        super(mappingProcess, self).__init__()

        # Variable Initialization
        self.args = args
        self.map_title = self.args[0]
        self.data_loc = self.args[1]
        self.plateDim = self.args[2]
        self.resolution = self.args[3]
        self.sampling = self.args[4]
        self.scheme = self.args[5]
        self.xcell = self.args[6]
        self.ycell = self.args[7]
        self.axis = self.args[8]
        self.commands = self.args[9]

        self.signals = mappingSignals()
        self.event_kill = threading.Event()

        # Initialization of virtual coordinates
        self.currX = 0
        self.currY = 0
        self.currAx = "xy"

        # Motor Variables
        self.motor = serial.Serial('COM1')
        self.motor.write(str.encode('DRIVE1011:'))
        self.motion_profile = ["MA 0X00:",  # Motion profile for serial communication with parker motors
                               "A 35,,50,50:",
                               "AA 17.500000,,25.000000,25.000000:",
                               "AD 35,,50,50:",
                               "ADA 17.500000,,25.000000,25.000000:",
                               "V 3,,4,4:",
                               "",  # Parker motor distance parameter; varies by command
                               "MC 0X00:"]

        # Data File Variables
        self.init_time = (datetime.now()).strftime("%m.%d.%Y_%H.%M.%S")

    @pyqtSlot()
    def kill_mapping_process(self):
        self.event_kill.set()

    @pyqtSlot()
    def run(self):  # Run block automatically called by threadPool() object
        self.signals.message.emit("Mapper thread successfully initialized.\n")
        time.sleep(1)

        """

        for i in range(5, 0, -1):  # Five minutes allotted for researchers to leave room
            if not i == 1:
                self.signals.message.emit("Mapping starts in " + str(i) + " minutes.\n")
            else:
                self.signals.message.emit("Mapping starts in 1 minute.\n")
            time.sleep(60)

        """

        # Data File Initialization
        if self.map_title == "default" or self.map_title == "":
            self.map_title = self.sampling + "_" + self.resolution + "_" + self.init_time + "_MAP"
        self.final_dest = os.path.join(self.data_loc, self.map_title)
        os.mkdir(self.final_dest)  # Creates directory for data files.        

        """
        info file
            general information on run, headers, etc

        master file
            contains every data point available
        """

        self.info_file = open(os.path.join(self.final_dest, "info.txt"), "w+")
        self.master_data = open(os.path.join(self.final_dest, "master.txt"), "w+")
        self.master_head = "\t\t\tPosition:\tAxis:\t\t\tField (pT):\t\tField stdev:\n"
        self.master_data.write(self.master_head)
        self.master_raw = open(os.path.join(self.final_dest, "master_raw.txt"), "w+")

        self.line_head = "Timestamp:\tPosition:\tYField (pT):\tYField stdev:\tZField (pT):\tZField stdev:\n"
        if self.scheme == "x-linear":  # Creates a text file for each line of measurements by the x-axis
            line_dict = []
            for i in range(1 + int((self.resolution.split("x"))[1])):
                line_dict = line_dict + [open(os.path.join(self.final_dest, ("line" + str(i) + ".txt")), "w+")]
                line_dict[i].write(self.line_head)
        elif self.scheme == "y-linear":
            row_dict = []
            for i in range(1 + int((self.resolution.split("x"))[0])):
                row_dict = row_dict + [open(os.path.join(self.final_dest, ("row" + str(i) + ".txt")), "w+")]
                row_dict[i].write(self.line_head)
        self.signals.message.emit("Data files successfully initialized.\n")

        # Motor Axis Initialization

        #self.home()

        # Probe with statement begins.

        self.signals.commandDone.emit()

        with serial.Serial(port='COM3', baudrate=115200, timeout=1) as probe:

            command_index = 0
            maxCommands = len(self.commands)
            while (not self.event_kill.is_set()):
                for command_index in range(maxCommands):
                    
                    command = self.commands[command_index]

                    if command == "Zero X Axis":
                        self.zeroX()
                    elif command == "Initialize probe.":
                        self.probeInitialize(probe)
                    elif command == "Home probe.":
                        self.home()
                        self.probeInitialize(probe)
                    elif command == "Zero Y Axis":
                        self.zeroY()
                    elif command == "Take Field Measurement":
                        self.measure(probe)
                    elif command == "Wait.":
                        time.sleep(1)
                    else:  # this else statement is meant to take care of both move functions and
                        self.com = command.split(" ")  # straggling empty lines that may appear in the pre-image
                        if self.com[0] == "Rotate":
                            self.rotate(self.com[2],probe)
                            self.mappass = True
                        if len(self.com) > 5:
                            if self.com[0] == "Move" and self.com[5] == "X":
                                self.moveX(int(self.com[1]))
                            elif self.com[0] == "Move" and self.com[5] == "Y":
                                self.moveY(int(self.com[1]))
                            elif len(self.com) == 3:
                                if self.com[1] == "to":
                                    self.dest = (self.com[2]).split(",")
                                    self.destX = (self.dest[0])[1:]
                                    self.destY = (self.dest[1])[:-1]
                                    self.moveXY(int(self.destX), int(self.destY))
                        else:
                            pass
               
                    self.signals.commandDone.emit()

                    #command_index = command_index + 1
                break 
            
        self.signals.message.emit("Map completed.\n")
        time.sleep(1)
        self.signals.message.emit("Extracting values from raw data.\n")

        """
        Following block performs first-order statistics on raw data.
        """

        self.master_raw.close()
        self.master_raw_readable = open(os.path.join(self.final_dest, "master_raw.txt"), "r")
        
        
        """
        Note: above block may seem redundant but without it the code does not work.
        There is a Python bug with reading and writing to the same file on windows...
        """        

        for package in (self.master_raw_readable.read()).split("######################################"):
            if len(package) > 10:
                # Extraction of data points
                raw_lines = package.split("\n")
                while "" in raw_lines:
                    raw_lines.remove("")
                raw_head = (raw_lines[0]).split(" ")
                raw_timestamp = raw_head[1] + " " + raw_head[2]
                raw_axis = raw_head[4]
                raw_coordinate = raw_head[6]
                rest = raw_lines[1:]
                pico_values = []
                for line in rest:
                    if (len(line) == 8) and (line[0] == "!"):
                        pico_values = pico_values + [self.fieldReading(line)]
                # First-Order Statistics
                raw_ave = round(stat.mean(pico_values), 2)
                raw_std = round(stat.pstdev(pico_values), 2)
                master_line = str(raw_timestamp) + "\t" + str(raw_coordinate) + "\t\t" + str(raw_axis)
                master_line = str(master_line) + "\t" + str(raw_ave) + "\t\t" + str(raw_std) + "\n"
                self.master_data.write(master_line)

            if self.scheme == "x-linear":
                raw_x = (raw_coordinate.split(","))[0][1:]
                line_dict[int(raw_x)].write(master_line)
            elif self.scheme == "y-linear":
                raw_y = (raw_coordinate.split(","))[1][:-1]
                line_dict[int(raw_y)].write(master_line)

        """
        
        Populate info file here!
        
        """
        self.signals.commandDone.emit()
    
#--------------------------------------------------------------------------------------------------------------#    
#-------------------------- MOTOR AND PROBE DEFINITIONS -------------------------------------------------------#
#--------------------------------------------------------------------------------------------------------------#

    #### Movement Functions

    """
    # old cooldown command ; now in moveMotors block #
    def cooldown(self, steps, axis):
        motvel = self.motion_profile[5]
        rps = (axis == 3) * motvel[7] + (axis == 4) * motvel[9] + (axis == 1) * 3
        rotations = abs(steps) / 4096
        waitTime = (rotations / rps) + 1 + 0.5 * (abs(steps) > 250 * 4096)
        time.sleep(round(waitTime, 3))
    """

    def moveMotors(self, dist1000, dist0010, dist0001):
        self.motion_profile[6] = "D"+str(dist1000)+",,"+str(dist0010)+","+str(dist0001)+":"
        for command in self.motion_profile:
            self.motor.write(str.encode(command))
        self.motor.write(str.encode("GO 1011:"))

        ### Cooldown Block

        motor_velocity = (self.motion_profile[5])[2:].split(",")
        travel_times = [abs(dist1000 / 4096) / 3,
                        abs(dist0010 / 4096) / int(str(motor_velocity[2])[0]),
                        abs(dist0001 / 4096) / int(str(motor_velocity[3])[0])]
        cooldown_time = (max(travel_times) + 1) * 1.1
        if dist0001 > 500000:
            cooldown_time = cooldown_time * 1.4
        time.sleep(cooldown_time)

    def home(self):
        self.signals.message.emit("Establishing mapping axes...\n")
        self.currX = 0
        self.currY = 0
        self.motion_profile[5] = "V 3.5,,2,2:"  # Reduces motor speed

        # X Axis

        self.moveMotors(0, -300000, 0)  # Hits negative limit switch.
        self.moveMotors(0, 6000, 0)  # Rezeroes X axis

        # Y Axis

        self.moveMotors(0, 0, -1100000)  # Hits negative y-limit switch
        self.moveMotors(0, 0, 6000)  # Rezeroes Y axis

        self.motion_profile[5] = "V 3.5,,4,4:"  # Returns motor speed to standard values
        self.signals.message.emit("Mapping axes established. Mapping begins.\n")

    def moveX(self, steps):
        ############### NO MOVEMENT PROTOCOL -- ignores moveMotor commands and waits 0.1s. Does not preserve "fake" coordinate data.
        #self.currX = self.currX + steps
        # dist_X = int(steps * float(self.xcell) * (4096 / 2))

        # if steps < 0:
        #     self.moveMotors(0, dist_X - 4000, 0)
        #     self.moveMotors(0, 4000, 0)
        # else:
        #     self.moveMotors(0, dist_X, 0)
        time.sleep(0.1)
        ###############


        self.signals.moveUpdate.emit([self.currX, self.currY])

    def moveY(self, steps):
        ############### NO MOVEMENT PROTOCOL -- ignores moveMotor commands and waits 0.1s. Does not preserve "fake" coordinate data.
        #self.currY = self.currY + steps
        # dist_Y = int(steps * float(self.ycell) * (4096 / 2))

        # if steps < 0:
        #     self.moveMotors(0, 0, dist_Y - 4000)
        #     self.moveMotors(0, 0, 4000)
        # else:
        #     self.moveMotors(0, 0, dist_Y)
        time.sleep(0.1)
        ###############

        self.signals.moveUpdate.emit([self.currX, self.currY])

    def moveXY(self, xdest, ydest):
        dist_X = int((xdest - self.currX) * self.xcell * (4096 / 2))
        dist_Y = int((ydest - self.currY) * self.ycell * (4096 / 2))
        self.moveMotors(0, dist_X, dist_Y)
        self.currX = xdest
        self.currY = ydest
        self.signals.moveUpdate.emit([self.currX, self.currY])

    def measure(self, probe):
        self.signals.measureUpdate.emit([self.currX, self.currY])

        if self.currAx == "xy":
            ax1 = "x"
            ax2 = "y1"
        else:
            ax1 = "z"
            ax2 = "y2"

        # First Axis Measurement
        probe.write(str.encode("@"))    # -> Sensors: Print Axis Y
        time.sleep(.5)
        self.flush(probe)
        time.sleep(.5)
        meas_buffer = probe.readlines(probe.in_waiting)
        self.saveRaw(ax1, meas_buffer)

        # Second Axis Measurement
        probe.write(str.encode("?"))    # -> Sensors: Print Axis Z
        time.sleep(.5)
        self.flush(probe)
        time.sleep(.5)
        meas_buffer = probe.readlines(probe.in_waiting)
        self.saveRaw(ax2, meas_buffer)

        self.flush(probe)

    def rotate(self, orient, probe):
        if self.currAx == orient:
            pass
        elif orient in ["xy", "yz"]:
            self.moveMotors(8192 * ((orient == "yz") - (orient == "xy")), 0, 0)
            self.currAx = orient
            self.fieldZero(probe)

    def zeroX(self):
        if self.currX > 0:
            self.moveX(-1 * self.currX)
        self.signals.moveUpdate.emit([self.currX, self.currY])

    def zeroY(self):
        if self.currY > 0:
            self.moveY(-1 * self.currY)
        self.signals.moveUpdate.emit([self.currX, self.currY])

    #### Probe Peripherals
    
    def probeInitialize(self, probe):
        self.signals.message.emit("Probe initializing...\n")
        
        self.signals.message.emit("Connection to probe established. Begin auto-start.\n")
        self.flush(probe)

        # Autostarting
        probe.write(str.encode(">"))  # -> Sensors: Autostart Mode Begin
        self.autocheck(probe, 1)
        
        self.fieldZero(probe)
        
    
    def fieldZero(self, probe):

        probe.write(str.encode("B"))  # -> Sensors: Dual Axis Mode
        self.signals.message.emit("Begin Field Zero.\n")
        probe.write(str.encode("D"))  # -> Sensors: Field Zero ON

        time.sleep(20)  # Probe Field Zeroing...
        self.flush(probe)  # Clearing buffer...
        time.sleep(5)  # Gathering measurements for zeroExtract()

        zero_buffer = probe.readlines(probe.in_waiting)
        self.flush(probe)
        self.zeroField = self.zeroExtract(zero_buffer)

        """ Nominally do something with the extracted zero value... """

        self.signals.message.emit("Field Zero Values: \n" + str(self.zeroField) + "\n")
        probe.write(str.encode("E"))  # -> Sensors: Field Zero OFF

        self.signals.message.emit("Probe calibration begins.\n")
        probe.write(str.encode("9"))  # -> Sensors: Calibration ON
        time.sleep(5)
        self.signals.message.emit("Calibration over.\n")
        probe.write(str.encode("7"))  # -> Sensors: Print ON
        time.sleep(10)
        self.flush(probe)
        self.signals.message.emit("Field Zeroing over. Command parsing resumes.\n")

    def flush(self, probe):
        probe.flushInput()
        probe.flushOutput()

    def fieldReading(self, reading):
        return round((float(reading[1:]) - 8388608) * 0.01, 2)

    def zeroReading(self, reading):
        if reading[2] == '7':
            b_zaxis = 'Bz'
        elif reading[2] == '8':
            b_zaxis = 'By'
        elif reading[2] == '9':
            b_zaxis = 'B0'
        else:
            b_zaxis = '?'
        return [b_zaxis, round(float(float(reading[3:]) - 32768), 2)]

    def zeroExtract(self, data_list):
        byZeroFound = False
        bzZeroFound = False
        b0ZeroFound = False
        by_zero = 0
        bz_zero = 0
        b0_zero = 0
        b_zero_index = len(data_list)
        while (b_zero_index > 1) and ((by_zero == 0) or (bz_zero == 0) or (b0_zero == 0)):
            b_zero_index = b_zero_index - 1
            
            if (data_list[b_zero_index].decode("utf-8"))[0] == "~":
                b_zero_line = self.zeroReading(data_list[b_zero_index].decode("utf-8"))
            else:
                b_zero_line = 'zero'
           
            if (b_zero_line[0] == 'By') and not byZeroFound:
                byZeroFound = True
                by_zero = b_zero_line[1]
            if (b_zero_line[0] == 'Bx') and not bzZeroFound:
                bzZeroFound = True
                bz_zero = b_zero_line[1]
            if (b_zero_line[0] == 'B0') and not b0ZeroFound:
                b0ZeroFound = True
                b0_zero = b_zero_line[1]
        return [by_zero, bz_zero, b0_zero]

    def autocheck(self, probe, index):
        self.signals.message.emit("Autocheck Attempt " + str(index)+"\n")
        if index > 5:
            self.signals.criticalError("Error: Auto start unsuccessful!\n")
            sys.exit()
        led1on = False
        led2on = False
        led3on = False
        bits_in_auto_buffer = probe.inWaiting()
        auto_buffer = probe.readlines(bits_in_auto_buffer)
        self.flush(probe)

        for line in auto_buffer:
            if line == b'|11\r\n':
                led1on = True
            elif line == b'|21\r\n':
                led2on = True
            elif line == b'|31\r\n':
                led3on = True

        if (led1on == True) and (led2on == True) and (led3on == True):
            self.signals.message.emit("Auto start successful.\n")
            pass
        else:
            time.sleep(20)
            self.autocheck(probe, index + 1)

    #### Data Handling

    def saveRaw(self, raw_ax, field_readings):
        coord_str = "(" + str(self.currX) + "," + str(self.currY) + ")"
        timestamp_for_raw = datetime.fromtimestamp(time.time()).strftime('%m/%d/%Y %H:%M:%S')
        raw_data_package = 'Time: ' + str(timestamp_for_raw) + " Axis: " + raw_ax + ' Coordinates: ' + coord_str + '\n'
        for entry in field_readings:
            raw_data_package = raw_data_package + entry.decode("utf-8")
        raw_data_package = raw_data_package + "######################################\n"
        self.master_raw.write(raw_data_package)





##########################################################################################################
#####################################       ADDITIONAL CLASSES        ####################################
##########################################################################################################




class timerProcess(QRunnable):

    def __init__(self, commands, xlen, ylen):

        super(timerProcess, self).__init__()

        self.commands = commands
        self.xlen = float(xlen)
        self.ylen = float(ylen)
        self.virtX = 0
        self.virtY = 0
        self.mappingTime = 60  # Homing command takes circa 1 minute
        self.signals = timerSignals()

    @pyqtSlot()
    def run(self):

        self.signals.message.emit("Calculating estimate mapping time...\n")
        for command in self.commands:
            VirtXMove = 0
            VirtYMove = 0
            if command == "Zero X Axis":
                VirtXMove = -1 * self.virtX
            elif command == "Zero Y Axis":
                VirtYMove = -1 * self.virtY
            elif command == "Wait.":
                self.mappingTime = self.mappingTime + 1
            else:  # this else statement is meant to take care of both move functions and
                self.cut_command = command.split(" ")  # straggling empty lines that may appear in the pre-image:
                if self.cut_command[0] == 'Rotate':
                    self.mappingTime = self.mappingTime + 2
                if len(self.cut_command) > 5:
                    if self.cut_command[0] == "Move" and self.cut_command[5] == "X":
                        VirtXMove = (int(self.cut_command[1]))
                    elif self.cut_command[0] == "Move" and self.cut_command[5] == "Y":
                        VirtYMove = (int(self.cut_command[1]))
                elif len(self.cut_command) == 3:
                    if self.cut_command[1] == "to":
                        self.virt_dest = (self.cut_command[2]).split(",")
                        self.virt_destX = (self.virt_dest[0])[1:]
                        self.virt_destY = (self.virt_dest[1])[:-1]
                        self.virtMoveXY(int(self.virt_destX), int(self.virt_destY))

            self.VirtXMove(VirtXMove)
            self.VirtYMove(VirtYMove)

        self.finalTime = round(self.mappingTime / 3600, 2)
        self.signals.message.emit("Estimated mapping time: " + str(self.finalTime) + " hours.\n")

    def VirtXMove(self, distance):
        self.mappingTime = self.mappingTime + self.xlen * abs(distance) / 10
        self.virtX = self.virtX + distance

    def VirtYMove(self, distance):
        self.mappingTime = self.mappingTime + self.ylen * abs(distance) / 10
        self.virtY = self.virtY + distance

    def virtMoveXY(self, destx, desty):
        virt_times = [self.xlen * abs(destx - self.virtX) / 10,
                      self.ylen * abs(desty - self.virtY) / 10]
        self.mappingTime = self.mappingTime + max(virt_times)
        self.virtX = destx
        self.virtY = desty


# Main GUI Window Object
class window(QMainWindow):
    def __init__(self):
        super(window, self).__init__()

        # Window Size Initialization

        self.windowWidth = 550
        self.windowHeight = 50
        self.windowX = 50
        self.windowY = 50
        self.setGeometry(self.windowX, self.windowY, self.windowWidth, self.windowHeight)
        self.setWindowTitle("F5 Mapper v. 0.99")

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.lay = QGridLayout(self.main_widget)

        self.loaded = False  # This variable keeps track whether a map has been loaded.

        self.threadpool = QThreadPool()  # Thread handler for main mapping process

        # Title Widgets

        self.title_label = QLabel("Title:")
        self.lay.addWidget(self.title_label, 0, 0)
        self.title_entry = QLineEdit()
        self.lay.addWidget(self.title_entry, 0, 1, 1, 2)
        self.title_button = QPushButton("Default")
        self.lay.addWidget(self.title_button, 0, 3)

        def title_default():
            self.title_entry.setText("default")

        self.title_button.clicked.connect(title_default)

        # Pre-Map Widgets

        self.premap_label = QLabel("Pre-Map:")
        self.lay.addWidget(self.premap_label, 1, 0)
        self.premap_entry = QLineEdit()
        self.lay.addWidget(self.premap_entry, 1, 1, 1, 2)
        self.premap_button = QPushButton("Browse...")
        self.lay.addWidget(self.premap_button, 1, 3)

        def premapBrowse():
            self.premap_entry.setText(
                str(QFileDialog.getOpenFileName(self, "Open Pre-Map", 'c:\\', "Pre-Map Files (*.txt)")[0]))

        self.premap_button.clicked.connect(premapBrowse)

        # Data Widgets

        self.data_label = QLabel("Data Path:")
        self.lay.addWidget(self.data_label, 2, 0)
        self.data_entry = QLineEdit()
        self.lay.addWidget(self.data_entry, 2, 1, 1, 2)
        self.data_button = QPushButton("Browse...")
        self.lay.addWidget(self.data_button, 2, 3)

        def dataBrowse():
            self.data_entry.setText(str(QFileDialog.getExistingDirectory(self, "Select Directory")))

        self.data_button.clicked.connect(dataBrowse)

        # Scheme Widgets

        self.scheme_label = QLabel("Data Scheme:")
        self.lay.addWidget(self.scheme_label, 3, 0)
        self.scheme_entry = QLineEdit()
        self.scheme_entry.setText("none")
        self.scheme_entry.setEnabled(False)
        self.scheme_value = False
        self.lay.addWidget(self.scheme_entry, 3, 1)
        self.scheme_button = QPushButton("Override")
        self.lay.addWidget(self.scheme_button, 3, 2)

        def schemeOverride():
            if self.scheme_value == False:
                self.scheme_entry.setEnabled(True)
                self.scheme_value = True
            else:
                self.scheme_entry.setEnabled(False)
                self.scheme_value = False
                if self.scheme_entry.text() in ["x-linear", "y-linear", "none"]:
                    self.scheme = self.scheme_entry.text()
                    self.comm("Data scheme successful override: " + self.scheme + "\n")
                else:
                    self.scheme_entry.setText(self.scheme)
                    self.comm("Error: invalid data scheme format.\n")

        self.scheme_button.clicked.connect(schemeOverride)

        # Comment Widgets

        self.comments_value = ""
        self.comments_button = QPushButton("Comments")
        self.lay.addWidget(self.comments_button, 3, 3)

        self.comments_clear = QPushButton("Clear")
        self.comments_submit = QPushButton("Submit")
        self.comments_entry = QTextEdit()

        def showComment():
            self.comments_dialog = QDialog(self)
            self.comments_dialog.move(100, 100)
            self.comments_lay = QGridLayout(self.comments_dialog)
            self.comments_dialog.setWindowTitle("Comments")
            self.comments_entry.setText(self.comments_value)
            self.comments_lay.addWidget(self.comments_entry, 0, 0, 1, 2)
            self.comments_lay.addWidget(self.comments_clear, 1, 0)
            self.comments_lay.addWidget(self.comments_submit, 1, 1)
            self.comments_dialog.show()

        def commentClear():
            self.comments_entry.setText("")

        self.comments_clear.clicked.connect(commentClear)

        def commentSubmit():
            self.comments_value = self.comments_entry.toPlainText()
            self.comments_dialog.accept()
            self.comments_dialog.hide()

        self.comments_submit.clicked.connect(commentSubmit)

        self.comments_button.clicked.connect(showComment)

        # Ticker Widgets

        self.commands = []

        self.ticker = QTextEdit()
        self.ticker.setReadOnly(True)
        self.lay.addWidget(self.ticker, 5, 3, 5, 1)
        self.ticker.setStyleSheet("background-color: rgb(0, 0, 0);"
                                  "color: rgb(18, 158, 14)")
        self.topticker = QLineEdit(self)
        self.topticker.setReadOnly(True)
        self.lay.addWidget(self.topticker, 4, 3)
        self.topticker.setStyleSheet("background-color: rgb(0, 0, 0);"
                                     "color: rgb(240, 0, 0)")
        self.topmessage = "Active command."
        self.dots = ""
        self.topticker.setText(" " + self.topmessage + self.dots)

        if len(self.commands) > 0:
            self.ticker.setText("\n".join(self.commands[1:]))
        else:
            self.ticker.setText("Commands.")

        # Progress Widgets

        self.progress_label = QLabel("Progress:")
        self.lay.addWidget(self.progress_label, 10, 0)
        self.progress_bar = QProgressBar()
        self.lay.addWidget(self.progress_bar, 10, 1, 1, 4)
        self.progress_bar.setEnabled(False)
        self.completed = 0

        # Map Widgets

        self.canvas = QPixmap(300, 550)
        self.canvas_label = QLabel()
        self.canvas_label.setPixmap(self.canvas)
        self.lay.addWidget(self.canvas_label, 4, 0, 6, 3)

        # Dialogue Widgets

        self.dial = ""
        self.dialogue = QTextEdit()
        self.dialogue.setReadOnly(True)
        self.lay.addWidget(self.dialogue, 11, 0, 1, 5)
        self.dialogue.setStyleSheet("background-color: rgb(0, 0, 0);"
                                    "color: rgb(18, 158, 14)")

        # Control Widgets

        self.help = QPushButton("Help")
        self.lay.addWidget(self.help, 12, 0)
        self.load = QPushButton("Load Map")
        self.lay.addWidget(self.load, 12, 1)
        self.kill = QPushButton("Kill Switch")
        self.lay.addWidget(self.kill, 12, 2)
        self.kill.setEnabled(False)
        self.runmap = QPushButton("Run Map")
        self.lay.addWidget(self.runmap, 12, 3, 1, 2)

        def LoadPreMap():
            if self.premap_entry.text() == "":
                self.comm("Error: Cannot load pre-map. No valid source path.\n")
            else:
                try:
                    self.premap = open(self.premap_entry.text(), "r").read()
                    self.topticker.setText("")
                    self.ticker.setText(self.premap.split("###############################\n")[1])
                    self.mapVars = self.premap.split("###############################\n")[0].split("\n")
                    self.maplen = len(self.ticker.toPlainText().split("\n"))
                    # Variable Initialization from premap file:
                    self.plateDims = self.mapVars[2].split(" ")[2]
                    self.resolution = self.mapVars[3].split(" ")[2]
                    self.sampling = self.mapVars[4].split(" ")[2]
                    self.scheme = self.mapVars[5].split(" ")[2]
                    self.xcell = self.mapVars[6].split(" ")[3]
                    self.ycell = self.mapVars[7].split(" ")[3]
                    self.axisMode = self.mapVars[8].split(" ")[2]
                    self.commands = (self.premap.split("###############################\n")[1]).split("\n")
                    self.loadComm = "Map loaded successfully with following parameters:\n" \
                                    "Plate Dimensions: " + self.plateDims + "\n" \
                                    "Map Resolution: " + self.resolution + "\n" \
                                    "Sampling Method: " + self.sampling + "\n" \
                                    "Data Scheme: " + self.scheme + "\n" \
                                    "X-Cell Length: " + self.xcell + "\n" \
                                    "Y-Cell Length: " + self.ycell + "\n" \
                                    "Axis Mode: " + self.axisMode + "\n"
                    self.comm(self.loadComm)
                    self.scheme_entry.setText(self.scheme)
                    # Variable Initialization for map image:
                    self.xRes = int(self.resolution.split("x")[0])
                    self.yRes = int(self.resolution.split("x")[1])
                    self.boxWidth = 10
                    self.boxHeight = 10
                    if not (((self.xRes + 4) * 10) < 300):
                        self.boxWidth = int(300 / (self.xRes + 4))
                    if not ((self.yRes + 4) * 10 < 550):
                        self.boxHeight = int(550 / (self.yRes + 4))
                    self.xStart = int((300 - self.xRes * self.boxWidth) / 2)
                    self.yStart = int((550 - self.yRes * self.boxHeight) / 2)
                    self.marked = []
                    self.mappass = False
                    self.current = [0, 0]
                    self.loaded = True
                    timer_thread = timerProcess(self.commands, self.xcell, self.ycell)
                    timer_thread.signals.message.connect(self.comm)
                    # Execution of timer thread.
                    self.threadpool.start(timer_thread)
                except:
                    self.comm("Error: Cannot load pre-map. Path syntax error.\n")
                self.mapUpdate()

        self.load.clicked.connect(LoadPreMap)

        def help():
            webbrowser.open("www.google.com")  ### Documentation goes here.

        self.help.clicked.connect(help)

        def startMap():
            if self.loaded and not self.title_entry.text() == "" and os.path.isdir(self.data_entry.text()) \
                    and self.scheme_entry.text() in ["x-linear", "y-linear", "none"]:
                self.comm("Initializing map...\n")
                self.title_entry.setEnabled(False)
                self.premap_entry.setEnabled(False)
                self.data_entry.setEnabled(False)
                self.scheme_entry.setEnabled(False)
                self.scheme_button.setEnabled(False)
                self.title_button.setEnabled(False)
                self.premap_button.setEnabled(False)
                self.data_button.setEnabled(False)
                self.comments_button.setEnabled(False)
                self.load.setEnabled(False)
                self.runmap.setEnabled(False)
                self.kill.setEnabled(True)
                # Initialization of mapping thread.
                vars_for_map_thread = [self.title_entry.text(), self.data_entry.text(), self.plateDims,
                                       self.resolution, self.sampling, self.scheme_entry.text(), self.xcell,
                                       self.ycell, self.axisMode, self.commands]
                map_thread = mappingProcess(vars_for_map_thread)
                map_thread.signals.message.connect(self.comm)
                map_thread.signals.measureUpdate.connect(self.measureUpdate)
                map_thread.signals.moveUpdate.connect(self.moveUpdate)
                map_thread.signals.commandDone.connect(self.tickerProg)
                map_thread.signals.commandDone.connect(self.updateBar)
                "map signal processing goes HERE"
                # Execution of mapping thread.
                self.threadpool.start(map_thread)
            else:
                if not self.loaded:
                    self.comm("Error: No map loaded.\n")
                else:
                    self.comm("Error: Missing parameters.\n")

        self.runmap.clicked.connect(startMap)

        def killMap():
            self.kill_dialog = QDialog(self)
            self.kill_dialog.move(150, 150)
            self.kill_lay = QGridLayout(self.kill_dialog)
            self.kill_dialog.setWindowTitle("Kill Process?")
            self.kill_label = QLabel("Are you sure? You will not be able to resume where you left off.\n")
            self.kill_lay.addWidget(self.kill_label, 0, 0, 1, 2)
            self.kill_yes = QPushButton("Abort")
            self.kill_yes.setStyleSheet("background-color: red")
            self.kill_no = QPushButton("Resume")
            self.kill_lay.addWidget(self.kill_yes, 1, 0)
            self.kill_lay.addWidget(self.kill_no, 1, 1)

            self.kill_yes.clicked.connect(yesKill)
            self.kill_yes.clicked.connect(map_thread.event_kill)

            self.kill_dialog.show()

        def yesKill():

            sys.exit()  # this is a placeholder until a smarter kill switch is implemented

            self.comm("Warning! Process manually cancelled mid-mapping!\n")
            self.comm("TS: " + (datetime.now()).strftime("%m/%d/%Y %H:%M:%S") + "\n")

            self.title_entry.setEnabled(True)
            self.premap_entry.setEnabled(True)
            self.data_entry.setEnabled(True)
            self.scheme_entry.setEnabled(True)
            self.scheme_button.setEnabled(True)
            self.title_button.setEnabled(True)
            self.premap_button.setEnabled(True)
            self.data_button.setEnabled(True)
            self.comments_button.setEnabled(True)
            self.load.setEnabled(True)
            self.runmap.setEnabled(True)
            self.kill.setEnabled(False)

        self.kill.clicked.connect(killMap)

        self.show()

    # Function to pass text to GUI text window, including error messages and progress reports.
    def comm(self, string):
        self.dial = string + self.dial
        self.dialogue.setText(self.dial)

    # Function to update map progress bar
    def updateBar(self):
        self.completed += (100 / self.maplen)
        self.progress_bar.setValue(int(self.completed))

    # Function to update map visualization
    def mapUpdate(self):
        self.canvas_label.setPixmap(QPixmap(300, 550))
        painter = QPainter(self.canvas_label.pixmap())
        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        painter.drawRect(0, 0, 300, 550)
        painter.setPen(QPen(Qt.green, 1, Qt.SolidLine))
        for i in range(self.xRes + 1):
            for j in range(self.yRes + 1):
                if [-1 * i + self.xRes, j] == self.current:
                    painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))
                elif [-1 * i + self.xRes, j] in self.marked:
                    if self.mappass == False:
                        painter.setBrush(QBrush(Qt.orange, Qt.SolidPattern))
                    if self.mappass == True:
                        painter.setBrush(QBrush(Qt.green, Qt.SolidPattern))                        
                else:
                    painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
                painter.drawRect(self.xStart + i * self.boxWidth, self.yStart + j * self.boxHeight,
                                 self.boxWidth, self.boxHeight)

    def measureUpdate(self):
        self.marked = self.marked + [self.current]

    def moveUpdate(self, point):
        self.current = point
        self.mapUpdate()

    def tickerProg(self):
        self.intermed_contents = (self.ticker.toPlainText()).split("\n")
        self.topticker.setText(self.intermed_contents[0])
        self.ticker.setText("\n".join(self.intermed_contents[1:]))


app = QApplication(sys.argv)
gui = window()
sys.exit(app.exec_())
