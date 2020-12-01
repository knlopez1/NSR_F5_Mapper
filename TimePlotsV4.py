# TimePlotsV4.py
# Author: Krystyna Lopez
# Last updated: 10/21/20
#
# Requires two input data file names in lines 24-28, ex.: 
# 	"simple_21x169_09.16.2020_15.28.34_MAP/mastery1.txt"
#	"ContinuousAlphaMap9-16-2020.txt"
#
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
map_file = "simple_21x169_09.17.2020_19.32.40_MAP"
map_loc = os.path.join(map_fold, map_file) 
axisfile2d = "mastery1.txt"
axisfile3d = "ContinuousAlphaMap9-17-2020_completed.txt"
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


#----------------------------------------------------------------------#
#opens the data files, parses the data, and stores it in arrays (lists)
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
#----------------------------------------------------------------------#


#Scaling 3D mapper values

j = 0
for i in range(len(reltimes3d)):
	if reltimes3d[i] == 0:
		j = i



Bx3d_scld = [round((float(x) - float(Bx3d[j]))*100000 + ((float(Bx3d[j])-(float(Bz3d[j])))/float(Bz3d[j])),7) for x in Bx3d]
By3d_scld = [round((float(x) - float(By3d[j]))*100000 + ((float(By3d[j])-(float(Bz3d[j])))/float(Bz3d[j])),7) for x in By3d]
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

	x = reltimes3d[0::60]
	y = y[0::60]

	spl = UnivariateSpline(x, y)
	spl.set_smoothing_factor(200000)
	Baxis3d_scld_spl = spl(reltimes3d)

	return(Baxis3d_scld_spl)


Bx3d_scld_spl = smooth_b_axis_data("Bx")
By3d_scld_spl = smooth_b_axis_data("By")
Bz3d_scld_spl = smooth_b_axis_data("Bz")


#------------------------------------------------------------------------------------------------------------------------------------------#
#Subtract scaled, smoothed background data from 2D mapper data


#This chunk of code was for subtracting specified values for X, Y, Z, but I don't think it's needed anymore with the new & improved optimization
"""
reltimes2d_exp = [''] * int(reltimes2d[-1] + 1)
pTvals2d_exp = [''] * int(reltimes2d[-1] + 1)

pTsubbed = []

#creates expanded arrays (lists) for the 2d mapper (this could be done better/more elegantly, just haven't cleaned it up yet)
for i in range(len(reltimes2d)):
	reltimes2d_exp[int(reltimes2d[i])] = reltimes2d[i]
	pTvals2d_exp[int(reltimes2d[i])] = pTvals2d[i]

X = 0
Y = 0
Z = 0

#creates an array (list) of subtracted pT values 
for i in range(len(pTvals2d_exp)):
	if pTvals2d_exp[i] != '':
		subfactor = (X * float(Bx3d_scld_spl[j+i])) + (Y * float(By3d_scld_spl[j+i])) + (Z * float(Bz3d_scld_spl[j+i]))
		pTsubval = float(pTvals2d_exp[i]) - subfactor
		#print(pTsubval)
		pTsubbed.append(pTsubval)
"""

Bx3d_scld_spl_trunc = []
By3d_scld_spl_trunc = []
Bz3d_scld_spl_trunc = []
reltimes3d_trunc = []

for i in range(len(reltimes2d)):
	for j in range(len(reltimes3d)):
		if reltimes2d[i] == reltimes3d[j]:
			reltimes3d_trunc.append(reltimes3d[j])
			Bx3d_scld_spl_trunc.append(float(Bx3d_scld_spl[j]))
			By3d_scld_spl_trunc.append(float(By3d_scld_spl[j]))
			Bz3d_scld_spl_trunc.append(float(Bz3d_scld_spl[j]))

pTvals2d_temp = [float(x) for x in pTvals2d]
pTvals2d_nparray = np.array(pTvals2d_temp)
reltimes3d_trunc_nparray = np.array(reltimes3d_trunc)
Bx3d_scld_spl_trunc = np.array(Bx3d_scld_spl_trunc)
By3d_scld_spl_trunc = np.array(By3d_scld_spl_trunc)
Bz3d_scld_spl_trunc = np.array(Bz3d_scld_spl_trunc)

def fun(params,array0,array1,array2,array3):
    a,b,c,d,e,f=params
    return (array0 + a*(array1+b) + c*(array2+d) + e*(array3+f)).dot(array0 + a*(array1+b) + c*(array2+d) + e*(array3+f))

res = minimize(fun,[0,0,0,0,0,0],method='SLSQP',args=(pTvals2d_nparray,Bz3d_scld_spl_trunc,Bx3d_scld_spl_trunc,By3d_scld_spl_trunc))

print(res)

resultarr = pTvals2d_nparray + res.x[0]*(Bz3d_scld_spl_trunc + res.x[1]) + res.x[2]*(Bx3d_scld_spl_trunc + res.x[3]) + res.x[4]*(By3d_scld_spl_trunc + res.x[5])


#------------------------------------------------------------------------------------------------------------------------------------------#
#For creating the array to make a heatmap
maxcoordx=0
maxcoordy=0

with open(mappath2d) as mp:
	for line in mp:
		elmt = line.split("\t")
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

myarray2 = np.zeros(shape=res)	

with open(mappath2d) as mp:
	i=0
	for line in mp:
		elmt = line.split("\t")
		coords = (elmt[1])[1:-1]
		coords = coords.split(",")
		coordx = int(coords[0])
		coordy = int(coords[1])

		myarray2[coordx,coordy] = resultarr[i]
		i += 1
	myarrayT2 = np.array(myarray2).T



#------------------------------------------------------------------------------------------------------------------------------------------#
#Putting arrays into DataFrames so that everything's in one place

#df2d = pd.DataFrame({'2D abs times': rawtimes2d, '2D rel times': reltimes2d, '2D coords': coords2d, 'pT': pTvals2d, 'St Dev': pTstdevs2d, 'pT subbed': pTsubbed})
df2d = pd.DataFrame({'2D abs times': rawtimes2d, '2D rel times': reltimes2d, '2D coords': coords2d, 'pT': pTvals2d, 'St Dev': pTstdevs2d})
df3d = pd.DataFrame({'3D rel times': reltimes3d, 'Bx scaled': Bx3d_scld,'By scaled': By3d_scld, 'Bz scaled': Bz3d_scld})
df3d_scal = pd.DataFrame({'3D abs times': rawtimes3d[:n], '3D rel times': reltimes3d[:n], 'Bx scaled': Bx3d_scld[:n],'By scaled': By3d_scld[:n], 'Bz scaled': Bz3d_scld[:n],
					'Bmod scaled': Bmod3d_scld[:n], 'Bx scaled splined': Bx3d_scld_spl,'By scaled splined': By3d_scld_spl,'Bz scaled splined': Bz3d_scld_spl})


# Assign an empty figure widget with multiple traces
trace2d = go.Scatter(x=df2d['2D rel times'], y=df2d['pT'], opacity=0.9, name='2D Plate Mapper')
trace3dx = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bx scaled'], opacity=0.2, name='3D Bartington Mapper X')
trace3dy = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['By scaled'], opacity=0.2, name='3D Bartington Mapper Y')
trace3dz = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bz scaled'], opacity=0.2, name='3D Bartington Mapper Z')
trace3dmod = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bmod scaled'], opacity=0.9, name='3D Bartington Mapper mod')
trace3dxint = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bx scaled splined'], opacity=0.9, name='3D Bartington Mapper X smoothed')
trace3dyint = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['By scaled splined'], opacity=0.9, name='3D Bartington Mapper Y smoothed')
trace3dzint = go.Scatter(x=df3d_scal['3D rel times'], y=df3d_scal['Bz scaled splined'], opacity=0.9, name='3D Bartington Mapper Z smoothed')
#tracesub = go.Scatter(x=df2d['2D rel times'], y=df2d['pT subbed'], opacity=0.9, name='2D Plate mapper subbed')
traceopt = go.Scatter(x=df2d['2D rel times'], y=resultarr, opacity=0.9, name='2D optimized')

hmy1 = sb.heatmap(myarrayT2, xticklabels=False, yticklabels=False, square=True, cbar_kws={'label':'pT'})
hmy1.invert_xaxis()

#Plot the data
g = go.FigureWidget(data=[trace2d, trace3dx, trace3dy, trace3dz, trace3dxint, trace3dyint, trace3dzint, traceopt],
                    layout=go.Layout(
                        title=dict(
                            text='Background Maps'
                        ),
                        barmode='overlay'
                    ))

#g.show()
plt.show()

