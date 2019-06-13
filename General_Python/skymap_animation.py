import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.basemap import Basemap
from astropy.time import Time
from astropy.coordinates import get_sun, get_moon, SkyCoord
import astropy.units as u
import pandas as pd
import os

def daylist_shao(StartUTC, EndinUTC):
	t0tmp = '2000-01-01'
	t1tmp = '2000-01-02'
	oneday = Time(t1tmp)-Time(t0tmp)
	Startday = Time(StartUTC,format='iso',scale='utc')
	Endinday = Time(EndinUTC,format='iso',scale='utc')
	deltaday = int((Endinday-Startday).jd)
	if deltaday == 0:
		sys.exit('***ERROR: StartUTC and EndinUTC are same!')
	elif deltaday == 1:
		daylist = [StartUTC, EndinUTC]
	elif deltaday >=2 :
		daylist = [StartUTC]
		for i in range(deltaday-1):
			anotherdaystr=(Startday+oneday*(i+1)).iso
			daylist.extend([anotherdaystr[0:10]])
		daylist.extend([EndinUTC])
	else:
		sys.exit('***ERROR: Check if StartUTC and EndinUTC are valid!')
	return daylist


StartUTC = '2010-01-01'
EndinUTC = '2019-01-01'
timestrs = daylist_shao(StartUTC,EndinUTC)
fig, ax = plt.subplots(figsize=(20,10))
projection = 'moll'
#ax.cla()	
map = Basemap(projection=projection, lat_0=0, lon_0=180,
		resolution='l', area_thresh=1000.0, celestial=True,ax=ax)
map.drawmeridians(np.arange(0, 360, 30), dashes=[1,0], color='#d9d6c3')
map.drawparallels(np.arange(-90, 90, 15), dashes=[1,0], labels=[1,0,0,1],
		          color='#d9d6c3',size=20)
map.drawmapboundary(fill_color='#f6f5ec')
if projection == 'moll':
	az1 = np.arange(0, 360, 30)
	zen1 = np.zeros(az1.size) + 2
	azname = []
	for i in az1:
		azname.append(r'${\/%s\/^{\circ}}$' % str(i))
	x1, y1 = map(az1, zen1)
	for index, value in enumerate(az1):
		plt.text(x1[index], y1[index], azname[index], size=20)
galactic_center=SkyCoord("0h 0d", frame='galactic').transform_to('icrs')
x,y=map(galactic_center.ra.deg, galactic_center.dec.deg)
map.plot(x, y, '*', color='red', markersize=10)
plt.text(x, y, '  Galactic Center', fontsize=10)

anti_galactic_center=SkyCoord("12h 0d", frame='galactic').transform_to('icrs')
x,y=map(anti_galactic_center.ra.deg, anti_galactic_center.dec.deg)
map.plot(x, y, '*', color='red', markersize=10)
plt.text(x, y, '  Anti-Galactic Center', fontsize=10)
for i in np.arange(0, 24, 0.2):
	galactic_plane=SkyCoord(str(i)+"h 0d", frame='galactic').transform_to('icrs')
	x,y=map(galactic_plane.ra.deg, galactic_plane.dec.deg)
	map.plot(x, y, '+', color='red', markersize=10)


for timestr in timestrs:
	time = Time(timestr)
	sun_position = get_sun(time)
	sun_x,sun_y = map(sun_position.ra.deg, sun_position.dec.deg)
	map.plot(sun_x, sun_y, 'o', color='#ffd400', markersize=5)
	#plt.text(sun_x, sun_y, ' sun', fontsize=10)
	moon_position = get_moon(time)
	moon_x,moon_y = map(moon_position.ra.deg, moon_position.dec.deg)
	map.plot(moon_x, moon_y, 'o', color='#72777b', markersize=5)
	#plt.text(moon_x, moon_y, ' moon', fontsize=10)
	ax.set_title("{}".format(timestr))
	plt.pause(0.01)
