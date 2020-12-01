#Code to make heat maps from individual axis data. 
#	Makes one image with all 4 axes side-by-side.

#INPUTS:
#	- map folder location (map_loc) and individual axis file names (xfile, etc.)

# ** TO BE USED FOR MAPS AFTER 9/27, WITH MAPPER VERSION UnstableMapperV9.py OR LATER
########################################################################################

import numpy as np
import plotly.express as px
from datetime import datetime
import pandas
import seaborn as sb
import matplotlib.pyplot as plt
import os

#np.set_printoptions(threshold=np.inf)  #for debugging; allows entire arrays to be viewed instead of being trucated.

map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file = "simple_21x169_09.16.2020_15.28.34_MAP"
map_loc = os.path.join(map_fold, map_file) 
xfile ="masterx.txt"														# individual axis file locations
y1file ="mastery1.txt"
zfile ="masterz.txt"
y2file ="mastery2.txt"
mapname = "Map Title: " + map_file



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

			if coordx > maxcoordx:
				maxcoordx = coordx
			if coordy > maxcoordy:
				maxcoordy = coordy	
		res = (maxcoordx + 1,maxcoordy + 1)

	myarrayT = np.array(myarray).T

	return(myarrayT)
	
#----------------------------------------------------------------------------------------------#

Xarray = makearray(xfile)				# populates each axis array with its respective pT data
Y1array = makearray(y1file)
Zarray = makearray(zfile)
Y2array = makearray(y2file)

fig, ax = plt.subplots(ncols=4)			# establishes subplots so all 4 can be plotted on one window
#cbar_ax = fig.add_axes([.91,.3,.03,.4])
#creates the heatmaps and assigns each one to a subplot

#New version working on for colorbar
"""
hmx = sb.heatmap(Zarray, xticklabels=False, yticklabels=False, square=True, ax=ax[0], cbar_ax=cbar_ax)
hmx.invert_xaxis()
hmy1 = sb.heatmap(Y1array, xticklabels=False, yticklabels=False, square=True, ax=ax[1])
hmy1.invert_xaxis()
hmz = sb.heatmap(Xarray, xticklabels=False, yticklabels=False, square=True, ax=ax[2])
hmz.invert_xaxis()
hmy2 = sb.heatmap(Y2array, xticklabels=False, yticklabels=False, square=True, ax=ax[3])
hmy2.invert_xaxis()
"""

#saved old version
hmx = sb.heatmap(Zarray, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[0])
hmx.invert_xaxis()
hmy1 = sb.heatmap(Y1array, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[1])
hmy1.invert_xaxis()
hmz = sb.heatmap(Xarray, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[2])
hmz.invert_xaxis()
hmy2 = sb.heatmap(Y2array, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'}, ax=ax[3])
hmy2.invert_xaxis()

ax[0].set_title("Z Axis")				# gives each subplot a title
ax[1].set_title("Y1 Axis")
ax[2].set_title("X Axis")
ax[3].set_title("Y2 Axis")

#for ax in axs

fig.suptitle('Heatmaps of Individual Probe Axes\n' + mapname, size=20)
fig.tight_layout()

#cbar = hmx.collections[0].colorbar
# here set the labelsize by 20
#cbar.ax.tick_params(labelsize=15)

plt.show()								#displays the plots
