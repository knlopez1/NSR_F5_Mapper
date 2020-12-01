
import numpy as np
import plotly.express as px
import datetime
import pandas
import seaborn as sb
import matplotlib.pyplot as plt
import os

np.set_printoptions(threshold=np.inf)
map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file = "simple_21x169_09.16.2020_15.28.34_MAP"
map_loc = os.path.join(map_fold, map_file) 
axisfile2d = "masterx.txt"
axisfile3d = "ContinuousAlphaMap9-16-2020.txt"
mappath2d = os.path.join(map_loc, axisfile2d) 
mappath3d = os.path.join(map_loc, axisfile3d)

origin = 0

"""
# ............................................................#
code that defines a "resolution" (array size) for heatmaps.
don't think I actually need for this application but it's here just in case.
def getres(mappath):
	with open(mappath) as mp:
		maxcoordx = 0
		maxcoordy = 0
		for line in mp:
			elmt = line.split("\t")
			# time = elmt[0].split(" ")[1]
			coords = (elmt[1])[1:-1]
			coords = coords.split(",")
			coordx = int(coords[0])
			coordy = int(coords[1])
			if coordx > maxcoordx:
				maxcoordx = coordx
			if coordy > maxcoordy:
				maxcoordy = coordy
		res = (maxcoordx + 1, maxcoordy + 1)
		return(res)
# ............................................................#
"""

def getlines(mappath):
	with open(mappath) as mp:
		lines = 0
		for line in mp:
			lines += 1
		return(lines)

lines2d = getlines(mappath2d)
lines3d = getlines(mappath3d)
res2d = (3, lines2d)
res3d = (3, lines3d)

rawtimes2d = [''] * lines2d
rawtimes3d = [''] * lines3d
#print(rawtimes2d)
#print(rawtimes3d)
maptimes2d = np.zeros(shape=res2d)
maptimes3d = np.zeros(shape=res3d)


with open(mappath2d) as mp:
	i = 0
	for line in mp:
		elmt = line.split("\t")
		coords = (elmt[1])[1:-1]
		coords = coords.split(",")
		coordx = int(coords[0])
		coordy = int(coords[1])
		pTval = elmt[4]
		dateandtime = elmt[0]
		date = dateandtime.split(" ")[0]
		mthdayyr = date.split("/")
		time = dateandtime.split(" ")[1]
		hrminsec = time.split(":")
		time2d = datetime.datetime(int(mthdayyr[2]), int(mthdayyr[0]), int(mthdayyr[1]), int(hrminsec[0]), int(hrminsec[1]), int(hrminsec[2]))
		rawtimes2d[i] = str(time2d)
		print(rawtimes2d[i])
		i += 1

with open(mappath3d) as mp:
	i = 0
	for line in mp:
		elmt = line.split(",")
		dateandtime = elmt[0]
		dandt = dateandtime.split(" ")
		month_name = dandt[1]
		dto = datetime.datetime.strptime(month_name, "%b")
		month_number = dto.month
		day_name = dandt[2]
		year = dandt[4]
		time = dandt[3]
		hrminsec = time.split(":")
		time3d = datetime.datetime(int(year), int(month_number), int(day_name), int(hrminsec[0]), int(hrminsec[1]), int(hrminsec[2]))
		rawtimes3d[i] = str(time3d)
		i += 1

#print(rawtimes2d)
#print(rawtimes3d)

# print((time2d-time3d).total_seconds())
if (time2d - time3d).total_seconds() < 0:
	origin = time2d
if (time2d - time3d).total_seconds() > 0:
	origin = time3d
#print(origin)



# (t-datetime.datetime(1970,1,1)).total_seconds()

# open the files again, parse the data, populate an array with (file time- origin time).totalseconds
