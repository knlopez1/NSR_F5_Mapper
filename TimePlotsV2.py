
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
import os

np.set_printoptions(threshold=np.inf)
map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file = "simple_21x169_09.16.2020_15.28.34_MAP"
map_loc = os.path.join(map_fold, map_file) 
axisfile2d = "mastery1.txt"
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

dtrawtimes2d = [''] * lines2d
dtrawtimes3d = [''] * lines3d
rawtimes2d = [''] * lines2d
rawtimes3d = [''] * lines3d
pTvals2d = [''] * lines2d
Bvals3d = [''] * lines3d

pTstdevs2d = [''] * lines2d
subvals = [''] * lines2d



with open(mappath2d) as mp:
	i = 0
	for line in mp:
		elmt = line.split("\t")
		coords = (elmt[1])[1:-1]
		coords = coords.split(",")
		coordx = int(coords[0])
		coordy = int(coords[1])
		pTval = elmt[4]
		pTstdev = elmt[6]
		dateandtime = elmt[0]
		date = dateandtime.split(" ")[0]
		mthdayyr = date.split("/")
		time = dateandtime.split(" ")[1]
		hrminsec = time.split(":")
		time2d = datetime.datetime(int(mthdayyr[2]), int(mthdayyr[0]), int(mthdayyr[1]), int(hrminsec[0]), int(hrminsec[1]), int(hrminsec[2]))
		dtrawtimes2d[i] = time2d
		pTvals2d[i] = pTval
		pTstdevs2d[i] = pTstdev
		#rawtimes2d[i] = str(time2d)
		i += 1

with open(mappath3d) as mp:
	i = 0
	for line in mp:
		elmt = line.split(",")
		dateandtime = elmt[0]
		Bval = elmt[6]
		#print(Bval)
		dandt = dateandtime.split(" ")
		month_name = dandt[1]
		dto = datetime.datetime.strptime(month_name, "%b")
		month_number = dto.month
		day_name = dandt[2]
		year = dandt[4]
		time = dandt[3]
		hrminsec = time.split(":")
		time3d = datetime.datetime(int(year), int(month_number), int(day_name), int(hrminsec[0]), int(hrminsec[1]), int(hrminsec[2]))
		dtrawtimes3d[i] = (time3d)
		Bvals3d[i] = Bval
		#print(Bvals3d[i])
		#rawtimes3d[i] = str(time3d)
		i += 1

Bvals3d = [float(x) for x in Bvals3d]
		


#print(Bvals3d)
origintime2d = dtrawtimes2d[0]
#print(origintime2d)
#reltime2d = [x for x in dtrawtimes2d]
reltimes2d = [(x - origintime2d).total_seconds() for x in dtrawtimes2d]
#print(reltime2d)
reltimes3d = [(x - origintime2d).total_seconds() for x in dtrawtimes3d]
#print(reltime3d)
#print(pTvals2d)

#print((time2d-time3d).total_seconds())
#starttime = time2d.total_seconds()

j = 0
for i in range(len(reltimes3d)):
	if reltimes3d[i] == 0:
		j = i
print(j)
Bvals3d = [round(float(x-Bvals3d[j]),7)*(100000) for x in Bvals3d]


for i in range(len(pTvals2d)):
	#val1 = pTvals2d[i]
	val2 = Bvals3d[j+i]
	val1 = (float(pTvals2d[i]))
	subvals[i] = val1 - val2
	print(subvals[i])
	#print(pTvals2d[i])
#print()


data1 = {'times2d': reltimes2d, 'pT values': pTvals2d, 'subvals': subvals}
data2 = {'times3d': reltimes3d, 'B values': Bvals3d}
df1 = pd.DataFrame(data1)
df2 = pd.DataFrame(data2)
# Assign an empty figure widget with two traces
trace1 = go.Scatter(x=df1['times2d'], y=df1['pT values'], opacity=0.75, name='2D Plate Mapper')
trace2 = go.Scatter(x=df2['times3d'], y=df2['B values'], opacity=0.75, name='3D Bartington Mapper')
trace3 = go.Scatter(x=df1['times2d'], y=df1['subvals'], opacity=0.75, name='2D - 3D')
g = go.FigureWidget(data=[trace1, trace2],
                    layout=go.Layout(
                        title=dict(
                            text='Background Maps'
                        ),
                        barmode='overlay'
                    ))

g.show()
#print(subvals)




# (t-datetime.datetime(1970,1,1)).total_seconds()

# open the files again, parse the data, populate an array with (file time- origin time).totalseconds