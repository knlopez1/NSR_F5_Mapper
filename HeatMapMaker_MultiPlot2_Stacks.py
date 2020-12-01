#Code to make heat maps from individual axis data. 
#	Makes one image with all 4 axes side-by-side.

#INPUTS:
#	- map folder location (map_loc) and individual axis file names (xfile, etc.)
########################################################################################

import numpy as np
import plotly.express as px
from datetime import datetime
import pandas
import seaborn as sb
import matplotlib.pyplot as plt
import os
import matplotlib.transforms as mtrans

#np.set_printoptions(threshold=np.inf)  #for debugging; allows entire arrays to be viewed instead of being trucated.

map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file1 = "simple_21x169_09.10.2020_20.09.08_MAP"
map_file2 = "simple_21x169_09.11.2020_18.35.10_MAP"
map_file3 = "simple_21x169_09.14.2020_18.57.53_MAP"
map_file4 = "simple_21x169_09.15.2020_16.55.11_MAP"

xfile ="masterx.txt"					# individual axis file locations
y1file ="mastery1.txt"
zfile ="masterz.txt"
y2file ="mastery2.txt"


#----------------------------------------------------------------------------------------------#

def makearray(axisfile):
	
	mappath = os.path.join(map_loc, axisfile)
	master_map = (((open(mappath, "r")).read()).split("\n"))[0:]
	
	#............................................................#
	#chunk of code to automatically calculate proper array sizes
	#based on coordinate data from the data file. 
	maxcoordx=0
	maxcoordy=0

	with open(mappath) as mp:
		for line in mp:
			elmt = line.split("\t")
			#time = elmt[0].split(" ")[1]
			coords = (elmt[1])[1:-1]
			coords = coords.split(",")
			coordx = int(coords[0])
			coordy = int(coords[1])
			if coordx > maxcoordx:
				maxcoordx = coordx
			if coordy > maxcoordy:
				maxcoordy = coordy	
		res = (maxcoordx + 1,maxcoordy + 1)
	#............................................................#

	myarray = np.zeros(shape=res)			# instantiates an array that will be filled with pT data for each axis.

	with open(mappath) as mp:
		for line in mp:
			elmt = line.split("\t")
			pTval = elmt[4]

			coords = (elmt[1])[1:-1]
			coords = coords.split(",")
			coordx = int(coords[0])
			coordy = int(coords[1])

			myarray[coordx,coordy] = pTval

	myarrayT = np.array(myarray).T

	return(myarrayT)
	
#----------------------------------------------------------------------------------------------#

map_file = map_file1
map_loc = os.path.join(map_fold, map_file) 
mapname = "Map Title: " + map_file
print(map_file)

Xarray1 = makearray(xfile)				# populates each axis array with its respective pT data
Y1array1 = makearray(y1file)
Zarray1 = makearray(zfile)
Y2array1 = makearray(y2file)

map_file=map_file2
map_loc = os.path.join(map_fold, map_file) 
mapname = "Map Title: " + map_file

Xarray2 = makearray(xfile)				# populates each axis array with its respective pT data
Y1array2 = makearray(y1file)
Zarray2 = makearray(zfile)
Y2array2 = makearray(y2file)

map_file=map_file3
map_loc = os.path.join(map_fold, map_file) 
mapname = "Map Title: " + map_file

Xarray3 = makearray(xfile)				# populates each axis array with its respective pT data
Y1array3 = makearray(y1file)
Zarray3 = makearray(zfile)
Y2array3 = makearray(y2file)

map_file=map_file4
map_loc = os.path.join(map_fold, map_file) 
mapname = "Map Title: " + map_file

Xarray4 = makearray(xfile)				# populates each axis array with its respective pT data
Y1array4 = makearray(y1file)
Zarray4 = makearray(zfile)
Y2array4 = makearray(y2file)

fig, ax = plt.subplots(nrows=4,ncols=4,sharey=True, figsize=(8,8))			# establishes subplots so all 4 can be plotted on one window

#creates the heatmaps and assigns each one to a subplot
heatmapx1 = sb.heatmap(Xarray1, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[0,0])
heatmapx1.invert_xaxis()
heatmapy11 = sb.heatmap(Y1array1, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[0,1])
heatmapy11.invert_xaxis()
heatmapz1 = sb.heatmap(Zarray1, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[0,2])
heatmapz1.invert_xaxis()
heatmapy21 = sb.heatmap(Y2array1, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[0,3])
heatmapy21.invert_xaxis()

heatmapx2 = sb.heatmap(Xarray2, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[1,0])
heatmapx2.invert_xaxis()
heatmapy12 = sb.heatmap(Y1array2, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[1,1])
heatmapy12.invert_xaxis()
heatmapz2 = sb.heatmap(Zarray2, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[1,2])
heatmapz2.invert_xaxis()
heatmapy22 = sb.heatmap(Y2array2, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[1,3])
heatmapy22.invert_xaxis()

heatmapx13 = sb.heatmap(Xarray3, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[2,0])
heatmapx13.invert_xaxis()
heatmapy13 = sb.heatmap(Y1array3, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[2,1])
heatmapy13.invert_xaxis()
heatmapz3 = sb.heatmap(Zarray3, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[2,2])
heatmapz3.invert_xaxis()
heatmapy23 = sb.heatmap(Y2array3, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[2,3])
heatmapy23.invert_xaxis()

heatmapx14 = sb.heatmap(Xarray4, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[3,0])
heatmapx14.invert_xaxis()
heatmapy14 = sb.heatmap(Y1array4, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[3,1])
heatmapy14.invert_xaxis()
heatmapz4 = sb.heatmap(Zarray4, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[3,2])
heatmapz4.invert_xaxis()
heatmapy24 = sb.heatmap(Y2array4, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[3,3])
heatmapy24.invert_xaxis()

ax[0,0].set_title("Z Axis")				# gives each subplot a title
ax[0,1].set_title("Y1 Axis")
ax[0,2].set_title("X Axis")
ax[0,3].set_title("Y2 Axis")
ax[0,0].set_ylabel("9/10\n null test plate\n dipole on", rotation=0, labelpad=50)
ax[1,0].set_ylabel("9/11\n null test plate\n dipole on", rotation=0, labelpad=50)
ax[2,0].set_ylabel("9/14\n null test plate\n dipole off", rotation=0, labelpad=50)
ax[3,0].set_ylabel("9/15\n no test plate", rotation=0, labelpad=50)


fig.suptitle('Heatmaps of Individual Probe Axes\n', size=18)
fig.tight_layout()
fig.subplots_adjust(hspace=0.03, wspace=0.05)

plt.show()								#displays the plots
