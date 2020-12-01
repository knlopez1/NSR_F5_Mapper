#Code that turns raw data into a processed data file, ex. YRawData.txt -> YData.txt.
###################################################################

import os 
import statistics as stat

map_title = "04_04_DualAxisTest"
data_loc = "/Users/Krystyna/Documents/IU/Research/F5 Mapper/Testing:Data/Background Test (Data and Analysis)/Dual-Axis Background Test Data"

final_dest = os.path.join(data_loc, map_title)

master_data = open(os.path.join(final_dest, "YData.txt"), "w+")

master_raw_readable = open(os.path.join(final_dest, "YRawData.txt"), "r")

def fieldReading(reading):
    return round((float(reading[1:]) - 8388608) * 0.01, 2) 

for package in (master_raw_readable.read()).split("######################################"):
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
                pico_values = pico_values + [fieldReading(line)]
        # First-Order Statistics
        raw_ave = round(stat.mean(pico_values), 2)
        raw_std = round(stat.pstdev(pico_values), 2)
        master_line = str(raw_timestamp) + "\t" + str(raw_coordinate) + "\t\t" + str(raw_axis)
        master_line = str(master_line) + "\t" + str(raw_ave) + "\t\t" + str(raw_std) + "\n"
        master_data.write(master_line)
