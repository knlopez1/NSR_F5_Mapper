#Code that turns raw data into a processed data file, ex. YRawData.txt -> YData.txt.
#Written for background data tests taken from March 2020 -> June 2020.
###################################################################

import os 
import statistics as stat

map_folder = "04_16_DualAxisTest"
map_folder_loc = "/Users/Krystyna/Documents/IU/Research/F5 Mapper/Testing:Data/Background Test (Data and Analysis)/Dual-Axis Background Test Data"

final_loc = os.path.join(map_folder_loc, map_folder)

master_data = open(os.path.join(final_loc, "YDataFakeCoords.txt"), "w+")      #name of file to write to

readfrom_filename = open(os.path.join(final_loc, "YRawData.txt"), "r")        #name of file data is extracted from

def fieldReading(reading):
    return round((float(reading[1:]) - 8388608) * 0.01, 2) 

i=0
j=0

for package in (readfrom_filename.read()).split("######################################"):
    if len(package) > 10:
        # Extraction of data points
        raw_lines = package.split("\n")
        while "" in raw_lines:
            raw_lines.remove("")
        raw_head = (raw_lines[0]).split(" ")
        raw_timestamp = raw_head[1] + " " + raw_head[2]
        raw_axis = "y"
        if i > 21:
            i=0
            j=j+1
        if j > 169:
            break
        raw_coordinate = str("(" + str(i) + "," + str(j) + ")")
        print(raw_coordinate)
        rest = raw_lines[1:]
        pico_values = []
        for line in rest:
            if (len(line) == 8) and (line[0] == "!"):
                pico_values = pico_values + [fieldReading(line)]
        # First-Order Statistics
        raw_ave = round(stat.mean(pico_values), 2)
        raw_std = round(stat.pstdev(pico_values), 2)
        master_line = str(raw_timestamp) + "\t" + raw_coordinate + "\t\t" + str(raw_axis)
        master_line = str(master_line) + "\t" + str(raw_ave) + "\t\t" + str(raw_std) + "\n"
        master_data.write(master_line)
        i=i+1
        
