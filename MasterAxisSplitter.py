#Code that splits a file with multiple axes into individual axis files.
#	Takes a master.txt file from a map and splits into individual axis 
#	files x, y1, z, and y2.
###################################################################

import os

map_title = "simple_21x169_10.08.2020_19.40.23_MAP"
data_loc = "/Users/Krystyna/Desktop"

final_dest = os.path.join(data_loc, map_title)

master_datax = open(os.path.join(final_dest, "masterx.txt"), "w+")
master_datay1 = open(os.path.join(final_dest, "mastery1.txt"), "w+")
master_dataz = open(os.path.join(final_dest, "masterz.txt"), "w+")
master_datay2 = open(os.path.join(final_dest, "mastery2.txt"), "w+")

with open(os.path.join(final_dest, "master.txt")) as mr:
	for line in mr:
		elmt = line.split("\t")
		print(elmt)
		if elmt[3] == "x":
			master_datax.write(line)
		elif elmt[3] == "y1":
			master_datay1.write(line)
		elif elmt[3] == "z":
			master_dataz.write(line)			
		elif elmt[3] == "y2":
			master_datay2.write(line)

