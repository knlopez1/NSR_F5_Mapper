# TimePlotsV3.py
# Author: Krystyna Lopez
# Last updated: 10/15/20
#
# Requires two input data file names in lines 24-28: 
# 	"simple_21x169_09.16.2020_15.28.34_MAP/mastery1.txt"
#	"ContinuousAlphaMap9-16-2020.txt"
#
# Hopefully will be able to select input files from a database rather than manually
# insert file names (as there will be >100 data sets in the coming months)
#########################################################################################

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import datetime
import pandas as pd
import seaborn as sb
import matplotlib.pyplot as plt
from scipy import interpolate
from scipy.interpolate import UnivariateSpline
from scipy.optimize import minimize
import os


map_fold = "/Users/Krystyna/Desktop/"  # folder where the map data is located
map_file = "simple_21x169_09.16.2020_15.28.34_MAP"
map_loc = os.path.join(map_fold, map_file) 
axisfile2d = "mastery1.txt"
axisfile3d = "ContinuousAlphaMap9-16-2020.txt"
mappath2d = os.path.join(map_loc, axisfile2d) 
mappath3d = os.path.join(map_loc, axisfile3d)


#Initializing arrays

rawtimes2d = []
coords2d = []
pTvals2d = []
pTstdevs2d = []

rawtimes3d = []
Bx3d = []
By3d = []
Bz3d = []
Bmod3d = []


#---------------------------------------------------------------#
#opens the data files, parses the data, and stores it in arrays
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
#---------------------------------------------------------------#



#Scaling 3D mapper values

j = 0
for i in range(len(reltimes3d)):
	if reltimes3d[i] == 0:
		j = i

Bx3d_scld = [round((float(x) - float(Bx3d[j]))*100000,7) for x in Bx3d]
By3d_scld = [round((float(x) - float(By3d[j]))*100000,7) for x in By3d]
Bz3d_scld = [round((float(x) - float(Bz3d[j]))*100000,7) for x in Bz3d]
Bmod3d_scld = [round((float(x) - float(Bmod3d[j]))*100000,7) for x in Bmod3d]


#Truncating 3D Mapper data so that it ends at the end time of the map

n = int(reltimes2d[-1]+(j+1))   	# n = the element in the reltimes3d array that gives the relative time in seconds that the map ends 

reltimes3d = reltimes3d[:n]			# redefines these arrays so they only contain data for the map time (cuts off part after map is done)
Bx3d_scld = Bx3d_scld[:n]
By3d_scld = By3d_scld[:n]
Bz3d_scld = Bz3d_scld[:n]
Bmod3d_scld = Bmod3d_scld[:n]



#------------------------------------------------------------------------------------------------------------------------------------------#
# Smoothing of background data 


def smooth_b_axis_data(axis):  	#input "axis" you want to smooth.

	if axis == "Bx":
		y = Bx3d_scld
	elif axis == "By":
		y = By3d_scld
	elif axis == "Bz":
		y = Bz3d_scld
	elif axis == "Bmod":
		y = Bmod3d_scld

	#plt.plot(reltimes3d, y, 'go', ms = 3)
	
	x = reltimes3d[0::60]
	y = y[0::60]

	#plt.plot(x, y, 'ro', ms = 6)
	spl = UnivariateSpline(x, y)
	spl.set_smoothing_factor(200000)
	Baxis3d_scld_spl = spl(reltimes3d)
	#plt.plot(reltimes3d, Baxis3d_scld_spl, 'bo', ms = 3)
	#plt.show()
	return(Baxis3d_scld_spl)

Bx3d_scld_spl = smooth_b_axis_data("Bx")
By3d_scld_spl = smooth_b_axis_data("By")
Bz3d_scld_spl = smooth_b_axis_data("Bz")


#------------------------------------------------------------------------------------------------------------------------------------------#
#Subtract scaled, smoothed background data from 2D mapper data


#reltimes2d_exp = [''] * int(reltimes2d[-1] + 1)
#pTvals2d_exp = [''] * int(reltimes2d[-1] + 1)

Bx3d_scld_spl_trunc = []
By3d_scld_spl_trunc = []
Bz3d_scld_spl_trunc = []

#for i in range(len(reltimes2d)):
#	reltimes2d_exp[int(reltimes2d[i])] = reltimes2d[i]
#	pTvals2d_exp[int(reltimes2d[i])] = pTvals2d[i]


#print(reltimes2d)
for i in range(len(reltimes2d)):
	for j in range(len(reltimes3d)):
		if reltimes2d[i] == reltimes3d[j]:
			Bx3d_scld_spl_trunc.append(Bx3d_scld_spl[j])
			By3d_scld_spl_trunc.append(By3d_scld_spl[j])
			Bz3d_scld_spl_trunc.append(Bz3d_scld_spl[j])

pTvals2d_nparray = np.array(pTvals2d)
Bx3d_scld_spl_trunc = np.array(Bx3d_scld_spl_trunc)
By3d_scld_spl_trunc = np.array(By3d_scld_spl_trunc)
Bz3d_scld_spl_trunc = np.array(Bz3d_scld_spl_trunc)
"""
def fun(params,array0,array1,array2,array3):
    a,b,c=params
    return abs(np.average(array0 - (a*array1 + b*array2 + c*array3)))

res = minimize(fun,[0,0,0],args=(pTvals2d_nparray,Bx3d_scld_spl_trunc,By3d_scld_spl_trunc,Bz3d_scld_spl_trunc))
#print(minfunc(arr0,x0[0],x0[1],x0[2]))
#res = minimize(minfunc, x0, args=(0.1,0.2,0.3))
#minarray = res.x 
print(res)

"""

#------------------------------------------------------------------------------------------------------------------------------------------#
#Putting arrays into DataFrames so that everything's in one place

df2d = pd.DataFrame({'2D abs times': rawtimes2d, '2D rel times': reltimes2d, '2D coords': coords2d, 'pT': pTvals2d, 'St Dev': pTstdevs2d, 'pT subbed': pTsubbed})
df3d = pd.DataFrame({'3D rel times': reltimes3d, 'Bx scaled': Bx3d_scld,'By scaled': By3d_scld, 'Bz scaled': Bz3d_scld})
df3d_scal = pd.DataFrame({'3D abs times': rawtimes3d[:n], '3D rel times': reltimes3d[:n], 'Bx scaled': Bx3d_scld[:n],'By scaled': By3d_scld[:n], 'Bz scaled': Bz3d_scld[:n],
					'Bmod scaled': Bmod3d_scld[:n], 'Bz scaled splined': Bz3d_scld_spl})


# Assign an empty figure widget with multiple traces
trace2d = go.Scatter(x=df2d['2D rel times'], y=df2d['pT'], opacity=0.9, name='2D Plate Mapper')
trace3dx = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bx scaled'], opacity=0.1, name='3D Bartington Mapper X')
trace3dy = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['By scaled'], opacity=0.1, name='3D Bartington Mapper Y')
trace3dz = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bz scaled'], opacity=0.9, name='3D Bartington Mapper Z')
trace3dmod = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bmod scaled'], opacity=0.9, name='3D Bartington Mapper mod')
trace3dzint = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bz scaled splined'], opacity=0.9, name='3D Bartington Mapper Z smoothed')
tracesub = go.Scatter(x=df2d['2D rel times'], y=df2d['pT subbed'], opacity=0.9, name='2D Plate mapper subbed')


#Plot the data
g = go.FigureWidget(data=[trace2d, trace3dx, trace3dy, trace3dz, trace3dzint, tracesub],
                    layout=go.Layout(
                        title=dict(
                            text='Background Maps'
                        ),
                        barmode='overlay'
                    ))

g.show(renderer="iframe")

