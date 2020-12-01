
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.interpolate import UnivariateSpline
import os

dumb_variable_that_isnt_used = 7
map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file = "simple_21x169_09.16.2020_15.28.34_MAP"
map_loc = os.path.join(map_fold, map_file) 
axisfile2d = "mastery1.txt"
axisfile3d = "ContinuousAlphaMap9-16-2020.txt"
mappath2d = os.path.join(map_loc, axisfile2d) 
mappath3d = os.path.join(map_loc, axisfile3d)


#Initializing arrays

rawtimes2d = []
#reltimes2d = [] don't actually need to define here 
coords2d = []
pTvals2d = []
pTstdevs2d = []

rawtimes3d = []
#reltimes3d = [] don't actually need to define here
Bx3d = []
By3d = []
Bz3d = []
Bmod3d = []


with open(mappath2d) as mp:
	for line in mp:
		elmt = line.split("\t")

		coordsraw = (elmt[1])[1:-1]
		coords = coordsraw.split(",")
		coordx = int(coords[0])
		coordy = int(coords[1])

		pTval = elmt[4]
		pTstdev = elmt[6].strip()

		dateandtime = elmt[0]
		date = dateandtime.split(" ")[0]
		mthdayyr = date.split("/")
		time = dateandtime.split(" ")[1]
		hrminsec = time.split(":")
		time2d = datetime.datetime(int(mthdayyr[2]), int(mthdayyr[0]), int(mthdayyr[1]), int(hrminsec[0]), int(hrminsec[1]), int(hrminsec[2]))

		rawtimes2d.append(time2d)
		coords2d.append(elmt[1])
		pTvals2d.append(pTval)
		pTstdevs2d.append(pTstdev)


with open(mappath3d) as mp:
	i = 0
	for line in mp:
		elmt = line.split(",")
		
		dandt = elmt[0]
		dandt = dandt.split(" ")
		month_name = dandt[1]
		dto = datetime.datetime.strptime(month_name, "%b")
		month_number = dto.month
		day_name = dandt[2]
		year = dandt[4]
		time = dandt[3]
		hrminsec = time.split(":")
		time3d = datetime.datetime(int(year), int(month_number), int(day_name), int(hrminsec[0]), int(hrminsec[1]), int(hrminsec[2]))

		Bvalx = elmt[4]
		Bvaly = elmt[5]
		Bvalz = elmt[6]
		Bvalmod = elmt[7]

		rawtimes3d.append(time3d)
		Bx3d.append(Bvalx)
		By3d.append(Bvaly)		
		Bz3d.append(Bvalz)
		Bmod3d.append(Bvalmod)

starttime = rawtimes2d[0]

reltimes2d = [(x-starttime).total_seconds() for x in rawtimes2d]
reltimes3d = [(x-starttime).total_seconds() for x in rawtimes3d]

#Scaling 3D mapper values

j = 0
for i in range(len(reltimes3d)):
	if reltimes3d[i] == 0:
		j = i

Bx3d_scld = [round((float(x) - float(Bx3d[j]))*100000,7) for x in Bx3d]
By3d_scld = [round((float(x) - float(By3d[j]))*100000,7) for x in By3d]
Bz3d_scld = [round((float(x) - float(Bz3d[j]))*100000,7) for x in Bz3d]
Bmod3d_scld = [round((float(x) - float(Bmod3d[j]))*100000,7) for x in Bmod3d]


n = int(reltimes2d[-1]+j)
x = reltimes3d[:n]
x1 = x[0::500]
y = Bz3d_scld[:n]
y1 = y[0::500]
plt.plot(x, y, 'go', ms = 3)
plt.plot(x1, y1, 'ro', ms = 6)
f = interpolate.interp1d(x1, y1, kind='cubic', fill_value='extrapolate')

xnew = reltimes3d[:n]
xnew = xnew[0::50]
Bz3d_scld_int = f(xnew)

plt.plot(xnew, Bz3d_scld_int, 'bo', ms = 3)

spl = UnivariateSpline(x1, y1)
#spl = UnivariateSpline(xnew, Bz3d_scld_int)
spl.set_smoothing_factor(4000)
#spl.set_smoothing_factor(40000)

Bz3d_scld_int_spl = spl(xnew)

plt.plot(xnew, Bz3d_scld_int_spl, 'yo', ms = 3)

plt.show()
