# created by Jin-Hang Zou
# Jun 22, 2018
# modified by Shao

import numpy as np
import sys
import re
from glob import glob
import matplotlib.pyplot as plt
from collections import OrderedDict
import astropy.units as u
from mpl_toolkits.basemap import Basemap
from astropy.table import Table
from astropy.coordinates import get_sun,get_body_barycentric,cartesian_to_spherical
from astropy.coordinates import SkyCoord, cartesian_to_spherical
from astropy.time import Time
from astropy.io import fits
from spherical_geometry.polygon import SphericalPolygon



class GBM_detector(object):
	def __init__(self,name,quaternion):
		self.name = name
		self.quaternion = quaternion

		self.position = self.get_position()
		#print(self.position)
		#self.gbm_xyz = np.array([0,0,1.0])
		p_lon = cartesian_to_spherical(self.position[0],self.position[1],self.position[2])[2].deg
		p_lat = cartesian_to_spherical(self.position[0],self.position[1],self.position[2])[1].deg
		#print(p_lon,p_lat)
		self.center = SkyCoord(ra = p_lon,dec = p_lat,frame = 'icrs',unit = 'deg')
		#print(self.center)

	def get_position(self):
		X = np.mat(self.gbm_xyz).T
		mat0 = self.get_mat(self.quaternion[0],self.quaternion[1],self.quaternion[2],self.quaternion[3])
		X1 = mat0*X
		x = np.array([X1[0],X1[1],X1[2]])
		x = np.array([x[0][0][0],x[1][0][0],x[2][0][0]])
		return x
	def get_mat(self,p1,p2,p3,p0):
		mat = np.mat(np.zeros((3, 3)))
		mat[0, 0] = p0 ** 2 + p1 ** 2 - p2 ** 2 - p3 ** 2
		mat[0, 1] = 2 * (p1 * p2 - p0 * p3)
		mat[0, 2] = 2 * (p0 * p2 + p1 * p3)
		mat[1, 0] = 2 * (p3 * p0 + p2 * p1)
		mat[1, 1] = p0 ** 2 + p2 ** 2 - p3 ** 2 - p1 ** 2
		mat[1, 2] = 2 * (p2 * p3 - p1 * p0)
		mat[2, 0] = 2 * (p1 * p3 - p0 * p2)
		mat[2, 1] = 2 * (p0 * p1 + p3 * p2)
		mat[2, 2] = p0 ** 2 + p3 ** 2 - p1 ** 2 - p2 ** 2
		return mat
	def get_fov(self,radius):
		if radius >= 60:
			steps = 5000 ## could be modified to speed up the plotting
		elif radius >= 30:
			steps = 400 ## could be modified to speed up the plotting
		else:
			steps = 100 ## could be modified to speed up the plotting
		j2000 = self.center.icrs
		poly = SphericalPolygon.from_cone(j2000.ra.value,j2000.dec.value,radius,steps = steps)
		re =  [p for p in poly.to_radec()][0]
		return re
	def contains_point(self,point):

		steps = 300
		j2000 = self.center.icrs
		poly = SphericalPolygon.from_cone(j2000.ra.value,j2000.dec.value,self.radius,steps = steps)
		return poly.contains_point(point.cartesian.xyz.value)

class NaI0(GBM_detector):

	def __init__(self,quaternion,point = None):
		self.az = 45.89
		self.zen = 90 - 20.58
		self.radius = 60.0
		self.gbm_xyz = np.array([0.2446677589,0.2523893824,0.9361823057])
		super(NaI0, self).__init__('n0',quaternion)


class NaI1(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 45.11
		self.zen = 90 - 45.31
		self.radius = 60.0
		self.gbm_xyz = np.array([0.5017318971,0.5036621127,0.7032706462])
		super(NaI1, self).__init__('n1', quaternion)


class NaI2(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 58.44
		self.zen = 90 - 90.21
		self.radius = 60.0
		self.gbm_xyz = np.array([0.5233876659,0.8520868147,-0.0036651682])
		super(NaI2, self).__init__('n2', quaternion)


class NaI3(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 314.87
		self.zen = 90 - 45.24
		self.radius = 60.0
		self.gbm_xyz = np.array([0.5009495177,-0.5032279093,0.7041386753])
		super(NaI3, self).__init__('n3', quaternion)


class NaI4(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 303.15
		self.zen = 90. - 90.27
		self.radius = 60.0
		self.gbm_xyz = np.array([ 0.5468267487,-0.8372325378,-0.0047123847])
		super(NaI4, self).__init__('n4', quaternion)


class NaI5(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 3.35
		self.zen = 90 - 89.97
		self.radius = 60.0
		self.gbm_xyz = np.array([0.9982910766,0.0584352143,0.0005236008])
		super(NaI5, self).__init__('n5', quaternion)


class NaI6(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 224.93
		self.zen = 90 - 20.43
		self.radius = 60.0
		self.gbm_xyz = np.array([-0.2471260191,-0.2465229020,0.9370993606])
		super(NaI6, self).__init__('n6', quaternion)



class NaI7(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 224.62
		self.zen = 90 - 46.18
		self.radius = 60.0
		self.gbm_xyz = np.array([-0.5135631636,-0.5067957667,0.6923950822])
		super(NaI7, self).__init__('n7', quaternion)
class NaI8(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az =  236.61
		self.zen = 90 - 89.97
		self.radius = 60.0
		self.gbm_xyz = np.array([-0.5503349679,-0.8349438131,0.0005235846])
		super(NaI8, self).__init__('n8', quaternion)

class NaI9(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 135.19
		self.zen = 90 - 45.55
		self.radius = 60.0
		self.gbm_xyz = np.array([-0.5064476761,0.5030998708,0.7002865795])
		super(NaI9, self).__init__('n9', quaternion)


class NaIA(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 123.73
		self.zen = 90 - 90.42
		self.radius = 60.0
		self.gbm_xyz = np.array([-0.5552650628,0.8316411478,-0.0073303046])
		super(NaIA, self).__init__('na', quaternion)

class NaIB(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 183.74
		self.zen = 90 - 90.32
		self.radius = 60.0
		self.gbm_xyz = np.array([-0.9978547710,-0.0652279514,-0.0055850266])
		super(NaIB, self).__init__('nb', quaternion)

class BGO0(GBM_detector):

	def __init__(self,quaternion,point = None):
		self.az = 0.0
		self.zen = 0.0
		self.radius = 90.0
		self.gbm_xyz = np.array([1.0,0.0,0.0])
		super(BGO0, self).__init__('b0',quaternion)


class BGO1(GBM_detector):

	def __init__(self, quaternion, point=None):
		self.az = 180.0
		self.zen = 0.0
		self.radius = 90.0
		self.gbm_xyz = np.array([-1.0,0.0,0.0])
		super(BGO1, self).__init__('b1', quaternion)



class GBMtime(object):
	def __init__(self):
		self.utc_start_time = '2008-08-07T03:35:44.0'
		self.mjd_start_time = 51910

	@classmethod

	def met_to_utc(self,met):
		if (met <= 54832.00000000):
			utc_tt_diff = 65.184
		elif (met <= 56109.00000000):
			utc_tt_diff = 66.184
		elif (met <= 57204.00000000):
			utc_tt_diff = 67.184
		elif (met <=  57754.00000000):
			utc_tt_diff = 68.184
		else:
			utc_tt_diff = 69.184

		mjdutc = ((met - utc_tt_diff) / 86400.0) + 51910 + 0.0007428703703
		met1 = Time(mjdutc,scale= 'utc',format = 'mjd')

		return met1

	@classmethod

	def utc_to_met(self,utc0):
		tt_time = Time(utc0, format='fits', scale='utc').mjd
		mmt = (tt_time - 0.0007428703703 - 51910) * 86400.0
		if mmt <= (252460801.000 - 65.184):
			dt = 65.184
		elif mmt <= (362793602.000 - 66.184):
			dt = 66.184
		elif mmt <= (457401603.000 - 67.184):
			dt = 67.184
		elif mmt <= (504921604.000 - 68.184):
			dt = 68.184
		else:
			dt = 69.184
		met = mmt + dt
		return met

	@classmethod

	def utc_time(self,utc0):
		tt = Time(utc0,format = 'fits',scale = 'utc')
		return tt





class GBM(object):
	'''
	Main funtion
	'''
	def __init__(self,quaternion,sc_pos = None,gbm_time = None):
		if gbm_time is not None:
			if (isinstance(gbm_time, str)):
				self.time = GBMtime.utc_time(gbm_time)
			else:
				self.time = GBMtime.met_to_utc(gbm_time)
		else:
			self.time = None
		self.n0 = NaI0(quaternion)
		self.n1 = NaI1(quaternion)
		self.n2 = NaI2(quaternion)
		self.n3 = NaI3(quaternion)
		self.n4 = NaI4(quaternion)
		self.n5 = NaI5(quaternion)
		self.n6 = NaI6(quaternion)
		self.n7 = NaI7(quaternion)
		self.n8 = NaI8(quaternion)
		self.n9 = NaI9(quaternion)
		self.na = NaIA(quaternion)
		self.nb = NaIB(quaternion)
		self.b0 = BGO0(quaternion)
		self.b1 = BGO1(quaternion)
		self.detectors = OrderedDict(n0=self.n0,n1=self.n1,n2=self.n2,n3=self.n3,n4=self.n4,n5=self.n5,n6=self.n6,n7=self.n7,n8=self.n8,n9=self.n9,na=self.na,nb=self.nb,b0=self.b0,b1=self.b1)
		self.NaI_detectors = OrderedDict(n0=self.n0,n1=self.n1,n2=self.n2,n3=self.n3,n4=self.n4,n5=self.n5,n6=self.n6,n7=self.n7,n8=self.n8,n9=self.n9,na=self.na,nb=self.nb)
		self.BGO_detectors = OrderedDict(b0=self.b0,b1=self.b1)
		self.quaternion = quaternion
		self.sc_pos = sc_pos


	def get_centers(self,NaI = True,BGO = True):
		centers = {}
		if(NaI):
			for key in self.NaI_detectors.keys():
				centers[self.NaI_detectors[key].name] = self.NaI_detectors[key].center
		if(BGO):
			for key in self.BGO_detectors.keys():
				centers[self.BGO_detectors[key].name] = self.BGO_detectors[key].center
		return centers

	def get_good_centers(self,point = None,NaI = True,BGO = True):
		if point is not None:
			centers = {}
			if(NaI):
				for key in self.NaI_detectors.keys():
					if(self.NaI_detectors[key].contains_point(point)):
						centers[self.NaI_detectors[key].name] = self.NaI_detectors[key].center
			if(BGO):
				for key in self.BGO_detectors.keys():
					if(self.BGO_detectors[key].contains_point(point)):
						centers[self.BGO_detectors[key].name] = self.BGO_detectors[key].center
			return centers
		else:
			sys.exit('No source position sepcified!')
			return False

	def get_fov(self,radius,NaI = True,BGO = True):

		polys = {}
		detector_list = []
		if(NaI):
			for key in self.NaI_detectors.keys():
				polys[self.NaI_detectors[key].name] = self.NaI_detectors[key].get_fov(radius)
				detector_list.append(key)
		if(BGO):
			for key in self.BGO_detectors.keys():
				polys[self.BGO_detectors[key].name] = self.BGO_detectors[key].get_fov(radius)
				detector_list.append(key)
		return detector_list,polys

	def get_good_fov(self,radius,point = None,NaI = True,BGO = True):
		if point is not None:
			polys = {}
			detector_list = []
			if(NaI):
				for key in self.NaI_detectors.keys():
					if(self.NaI_detectors[key].contains_point(point)):
						polys[self.NaI_detectors[key].name] = self.NaI_detectors[key].get_fov(radius)
						detector_list.append(key)
			if(BGO):
				for key in self.BGO_detectors.keys():
					if(self.BGO_detectors[key].contains_point(point)):
						polys[self.BGO_detectors[key].name] = self.BGO_detectors[key].get_fov(radius)
						detector_list.append(key)

			return detector_list,polys
		else:
			sys.exit('No source position sepcified!')
			return False

	def get_separation(self,source = None,NaI = True,BGO = True):

		tab = Table(names=["Detector", "Separation"], dtype=["|S2", np.float64])
		if source is not None:
			if(NaI):
				for key in self.NaI_detectors.keys():
					sep = self.NaI_detectors[key].center.separation(source)
					tab.add_row([key, sep])
			if(BGO):
				for key in self.BGO_detectors.keys():
					sep = self.BGO_detectors[key].center.separation(source)
					tab.add_row([key, sep])
			tab['Separation'].unit = u.degree
			tab.sort("Separation")
			return tab
		else:
			sys.exit('No source position sepcified!')
	def get_earth_point(self):
		if self.sc_pos is not None:
			self.calc_earth_points()
			return self.earth_points
		else:
			sys.exit('No SC position!')

	def calc_earth_points(self):
		xyz_position = SkyCoord(x=self.sc_pos[0],y=self.sc_pos[1],z=self.sc_pos[2],frame='icrs',representation='cartesian')
		earth_radius = 6371. * u.km
		fermi_radius = np.sqrt((self.sc_pos ** 2).sum())
		horizon_angle = 90 - np.rad2deg(np.arccos((earth_radius / fermi_radius).to(u.dimensionless_unscaled)).value)
		horizon_angle = (180 - horizon_angle) * u.degree
		num_points = 3000
		ra_grid_tmp = np.linspace(0, 360, num_points)
		dec_range = [-90, 90]
		cosdec_min = np.cos(np.deg2rad(90.0 + dec_range[0]))
		cosdec_max = np.cos(np.deg2rad(90.0 + dec_range[1]))
		v = np.linspace(cosdec_min, cosdec_max, num_points)
		v = np.arccos(v)
		v = np.rad2deg(v)
		v -= 90.
		dec_grid_tmp = v
		ra_grid = np.zeros(num_points ** 2)
		dec_grid = np.zeros(num_points ** 2)
		itr = 0
		for ra in ra_grid_tmp:
			for dec in dec_grid_tmp:
				ra_grid[itr] = ra
				dec_grid[itr] = dec
				itr += 1
		all_sky = SkyCoord(ra=ra_grid, dec=dec_grid, frame='icrs', unit='deg')
		condition = all_sky.separation(xyz_position) > horizon_angle
		self.earth_points = all_sky[condition]




	def detector_plot(self,radius = 60.0,point = None,good = False,projection = 'moll',lat_0 = 0,lon_0 = 180,map = None, NaI = True,BGO = True,show_bodies = False):
		
		map_flag = False

		if map is None:
			fig = plt.figure(figsize = (20,20))
			ax = fig.add_subplot(111)
			map = Basemap(projection=projection,lat_0=lat_0,lon_0 = lon_0,resolution = 'l',area_thresh=1000.0,celestial=True,ax = ax)
		else:
			map_flag = True

		if good and point:
			detector_list,fovs = self.get_good_fov(radius = radius,point = point,NaI = NaI,BGO = BGO)

		else:
			detector_list,fovs = self.get_fov(radius,NaI = NaI,BGO = BGO)
		if point:
			ra,dec = map(point.ra.value,point.dec.value)
			map.plot(ra,dec , '*', color='#f36c21' , markersize=20.)

		for key in detector_list:
			ra,dec = fovs[self.detectors[key].name]
			ra,dec = map(ra,dec)
			map.plot(ra,dec,'.',color = '#74787c',markersize = 3)
			x,y = map(self.detectors[key].center.icrs.ra.value,self.detectors[key].center.icrs.dec.value)
			plt.text(x-200000, y-200000,self.detectors[key].name, color='#74787c', size=22)
		if show_bodies and self.sc_pos is not None:
			earth_points = self.get_earth_point()
			lon, lat = earth_points.ra.value, earth_points.dec.value
			lon,lat = map(lon,lat)
			map.plot(lon, lat, ',', color="#0C81F9", alpha=0.1, markersize=4.5)
			if self.time is not None:
				earth_r = get_body_barycentric('earth',self.time)
				moon_r = get_body_barycentric('moon',self.time)
				r_e_m = moon_r - earth_r
				r = self.sc_pos -np.array([r_e_m.x.value,r_e_m.y.value,r_e_m.z.value])*u.km
				moon_point_d = cartesian_to_spherical(-r[0],-r[1],-r[2])
				moon_ra,moon_dec = moon_point_d[2].deg,moon_point_d[1].deg
				moon_point = SkyCoord(moon_ra,moon_dec,frame='icrs', unit='deg')
				moon_ra,moon_dec = map(moon_point.ra.deg,moon_point.dec.deg)
				map.plot(moon_ra,moon_dec,'o',color = '#72777b',markersize = 20)
				plt.text(moon_ra,moon_dec,'  moon',size = 20)
			if show_bodies and self.time is not None:
				tmp_sun = get_sun(self.time)
				sun_position = SkyCoord(tmp_sun.ra.deg,tmp_sun.dec.deg,unit='deg', frame='icrs')
				sun_ra,sun_dec = map(sun_position.ra.value,sun_position.dec.value)
				map.plot(sun_ra,sun_dec ,'o',color = '#ffd400',markersize = 40)
				plt.text(sun_ra-550000,sun_dec-200000,'sun',size = 20)


		if not map_flag:
			if projection == 'moll':
				az1 = np.arange(0, 360, 30)
				zen1 = np.zeros(az1.size) + 2
				azname = []
				for i in az1:
					azname.append(r'${\/%s\/^{\circ}}$' % str(i))
				x1, y1 = map(az1, zen1)
				for index, value in enumerate(az1):
					plt.text(x1[index], y1[index], azname[index], size=20)
			_ = map.drawmeridians(np.arange(0, 360, 30),dashes=[1,0],color='#d9d6c3')
			_ = map.drawparallels(np.arange(-90, 90, 15),dashes=[1,0], labels=[1,0,0,1], color='#d9d6c3',size = 20)
			map.drawmapboundary(fill_color='#f6f5ec')


def get_met_from_utc(time):
	tt_time = Time(time,format = 'isot',scale = 'utc').mjd
	mmt = (tt_time-0.0007428703703-51910)*86400.0
	if mmt <= (252460801.000 - 65.184):
		dt = 65.184
	elif mmt <= (362793602.000 - 66.184):
		dt = 66.184
	elif mmt <= (457401603.000 - 67.184):
		dt = 67.184
	elif mmt <= (504921604.000 - 68.184):
		dt = 68.184
	else:
		dt = 69.184
	met = mmt + dt
	return met



def get_pos_from_fit(file_link):
	f = fits.open(file_link)
	time = f[1].data.field(0)
	pos_x = f[1].data.field(8)
	pos_y = f[1].data.field(9)
	pos_z = f[1].data.field(10)
	return time,pos_x,pos_y,pos_z


def find_right_list_for_pos(file_link,met):
	time,pos_x,pos_y,pos_z = get_pos_from_fit(file_link)
	dt = (time - met)**2
	dt = np.array(dt)
	dtmin=dt.min()
	if dtmin >= 1: sys.exit('poshist file is not complete at (MET): '+met+file_link)
	index = np.where(dt == dtmin)
	pos = np.array([pos_x[index][0],pos_y[index][0],pos_z[index][0]])
	return pos


def earth_occultation_of_source(source,timelist,datadir):
	'''
	:param source:
	:param timelist:
	:return: a dict [ earth postion, separation of earth center and source, earth radius, bool for occultation]
	0 for occultation, 1 for non-occultation.
	'''
	c = {}
	for time in timelist:
		earth_position,radius = get_earth_for_fermi(time,datadir)
		a = [earth_position,earth_position.separation(source),radius]
		if a[1]<=radius:
			a.append(0)
		else:
			a.append(1)
		c[time] = a
	return c

def if_earth_occultation_shao(source,timestr,datadir):
	'''
	0 for occultation, 1 for non-occultation.
	'''
	earth_position,radius = get_earth_for_fermi(timestr,datadir)
	earth_sours_seps=earth_position.separation(source)
	if earth_sours_seps<=radius:
		ifvalue=0
	else:
		ifvalue=1
	return ifvalue

def get_earth_for_fermi(timestr,datadir):
	t=Time(timestr,format='iso',scale='utc')
	timestrisot=t.isot
	year=timestr[:4]
	yearshort=timestr[2:4]
	month=timestr[5:7]
	day=timestr[8:10]	
	localdir = datadir + year + '/' + month + '/' + day + '/'
	filef = 'glg_poshist_all_'+yearshort+month+day
	filelist = glob(localdir+filef+'*')
	if len(filelist) != 1:
		sys.exit('***ERROR:  check if '+filef+' is available***')
	filelink = filelist[0]
	met = get_met_from_utc(timestrisot)
	pos = find_right_list_for_pos(filelink,met)*u.m
	xyz_position = SkyCoord(x=pos[0],y=pos[1],z=pos[2],frame='icrs',representation='cartesian')
	earth_radius = 6371. * u.km
	fermi_radius = np.sqrt((pos ** 2).sum())
	horizon_angle = (90 - np.rad2deg(np.arccos((earth_radius / fermi_radius).to(u.dimensionless_unscaled)).value))*u.degree
	lenlat = cartesian_to_spherical(-xyz_position.x.value,-xyz_position.y.value,-xyz_position.z.value)
	earth_position = SkyCoord(lenlat[2].deg,lenlat[1].deg,frame='icrs',unit = 'deg')
	return earth_position,horizon_angle



