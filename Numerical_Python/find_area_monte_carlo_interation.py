import numpy as np
import matplotlib.pyplot as plt

def f1(x):
	"""up small circle"""
	return (5**2.0-(x-5.0)**2.0)**0.5+5.0

def f2(x):
	"""down small circle"""
	return -(5**2.0-(x-5.0)**2.0)**0.5+5.0

def f3(x):
	"""up big circle"""
	return (10**2.0-(x-10.0)**2.0)**0.5

def f4(x):
	"""down big circle"""
	return -(10**2.0-x**2.0)**0.5+10

x=np.linspace(0,10,201)

goodpoints_x = []
goodpoints_y = []
npoints = 1000000
d_x = np.random.uniform(0,10,npoints)
d_y = np.random.uniform(0,10,npoints)

for i in range(npoints):
	if ((f1(d_x[i]) > d_y[i] 
		and f2(d_x[i]) < d_y[i] 
		and f3(d_x[i]) < d_y[i]) or 
		(f2(d_x[i]) < d_y[i]
		and f4(d_x[i]) > d_y[i]
		and f1(d_x[i]) > d_y[i])):
		goodpoints_x.append(d_x[i])
		goodpoints_y.append(d_y[i])
'''
for i in range(npoints):
	if (f1(d_x[i]) > d_y[i] 
		and f2(d_x[i]) < d_y[i]):
		goodpoints_x.append(d_x[i])
		goodpoints_y.append(d_y[i])
'''

area=100.0*(len(goodpoints_x)/len(d_x))
print('my evaluated area=',area)

print('your wild guess=',25.0*np.pi/4)



fig = plt.figure(figsize=(10,10))
plt.plot(x,f1(x),color='green',lw=3,zorder=2)
plt.plot(x,f2(x),color='green',lw=3,zorder=2)
plt.plot(x,f3(x),color='green',lw=3,zorder=2)
plt.plot(x,f4(x),color='green',lw=3,zorder=2)
plt.scatter(goodpoints_x,goodpoints_y,color='blue',s=1)
plt.xlim([0,10])
plt.ylim([0,10])
plt.tick_params(labelsize=25)
plt.text(4,5,'area='+str(round(area,3)),fontsize=25,color='blue')
plt.text(2,4,'${{\pi R^2}/ 4}$='+str(round(25.0*np.pi/4,4))+' (not true)',fontsize=25,color='red')
plt.savefig('./find_area_solution.png')
