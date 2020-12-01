#Code to make heat maps from individual axis data. 
#	Makes an image with a heat map of one probe axis.

#INPUTS:
#	- map file location (map_fold, map_file, axisfile)
########################################################################################

import numpy as np
import plotly.express as px
from datetime import datetime
import pandas
import seaborn as sb
import matplotlib.pyplot as plt
import os

np.set_printoptions(threshold=np.inf)
map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file = "simple_21x169_09.27.2020_23.08.18_MAP"
map_loc = os.path.join(map_fold, map_file) 
axisfile = "mastery2.txt"
mappath = os.path.join(map_loc, axisfile) 
mapname = "Map Title: " + map_file + "/" + axisfile

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


myarray = np.zeros(shape=res)


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


heatmap = sb.heatmap(myarray, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT',"orientation": "horizontal"})
plt.text(85,-25,'Heatmap of Individual Probe Axis: "Y2 Axis" Map\n', fontsize = 'xx-large', color='Black', horizontalalignment='center')
plt.text(85,-24,'('+mapname+')', fontsize = 'large', color='Black', horizontalalignment='center')
#plt.title('Heatmap of Individual Probe Axis: "X Axis" Map\n' + mapname, y=1.5)

#plt.rc('text', usetex=True)
#plt.title('{\fontsize{30pt}{3em}\selectfont{}{Mean WRFv3.5 LHF\r}{\fontsize{18pt}{3em}\selectfont{}{(September 16 - October 30, 2012)}')

#heatmap.set_title('Heatmap of Individual Probe Axis\n' + mapname)
#12, -8
#fontsize = medium
plt.show()





