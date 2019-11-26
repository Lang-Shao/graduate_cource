#!/usr/bin/python3
#created by Jin-Hang Zou
#modified by Shao
#convert -delay 40 -resize 800x600 -loop 0 *.png animated.gif

from zjh_gbmgeometry import *
import os
from multiprocessing import Pool


def met2utc(myMET):
	UTC0=Time('2001-01-01',format='iso',scale='utc')
	if isinstance(myMET,(list,tuple,np.ndarray)):
		myMETsize=len(myMET)
		utc_tt_diff=np.zeros(myMETsize)
		#from Fermi MET to UTC
		# 4 leap seconds after 2007:
		#'2008-12-31 23:59:60' MET=252460801.000000
		#'2012-06-30 23:59:60' MET=362793602.000000
		#'2015-06-30 23:59:60' MET=457401603.000000
		#'2016-12-31 23:59:60' MET=504921604.000000
		for i in range(myMETsize):
			if myMET[i] < 239772945.000: # valid data start 9 weeks after the mission starts
				print('**** ERROR: One of the MET TIME is not valid!!! ****')
			elif myMET[i] <= 252460801.000:
				utc_tt_diff[i]=33.0
			elif myMET[i] <= 362793602.000:
				utc_tt_diff[i]=34.0
			elif myMET[i] <= 457401603.000:
				utc_tt_diff[i]=35.0
			elif myMET[i] <= 504921604.000:
				utc_tt_diff[i]=36.0
			else:
				utc_tt_diff[i]=37.0
		myTimeGPS=Time(np.array(myMET)+UTC0.gps-utc_tt_diff,format='gps')
		return myTimeGPS.iso
	elif np.isscalar(myMET):
		if myMET < 239772945.000: # valid data start 9 weeks after the mission starts
			print('**** ERROR: One of the MET TIME is not valid!!! ****')
		elif myMET <= 252460801.000:
			utc_tt_diff=33.0
		elif myMET <= 362793602.000:
			utc_tt_diff=34.0
		elif myMET <= 457401603.000:
			utc_tt_diff=35.0
		elif myMET <= 504921604.000:
			utc_tt_diff=36.0
		else:
			utc_tt_diff=37.0
		myTimeGPS=Time(myMET+UTC0.gps-utc_tt_diff,format='gps')
		return myTimeGPS.iso
	else:
		print('Check your input format!')
		return None

def utc2met(myUTCstring):
	print(' ')
	print('myUTC=')
	for value in myUTCstring:
		print(value)
	UTC0=Time('2001-01-01',format='iso',scale='utc')
	myUTC=Time(myUTCstring,format='iso',scale='utc')
	datastart='2008-08-07 03:35:44.0' # valid data start 9 weeks after the mission starts 
	datastartUTC=Time(datastart,format='iso',scale='utc')
	if((myUTC<datastartUTC).any()):
			print('**** ERROR: One of the UTC TIME is not valid!!! ****: ',myUTCstring)
	#print('output MET=')
	#for value in myUTC.gps-UTC0.gps:
	#	print("%.5f" % value)
	return myUTC.gps-UTC0.gps


def open_fit(file_link):
	f = fits.open(file_link)
	time = f[1].data.field(0)
	qsj1 = f[1].data.field(1)
	qsj2 = f[1].data.field(2)
	qsj3 = f[1].data.field(3)
	qsj4 = f[1].data.field(4)
	pos_x = f[1].data.field(8)
	pos_y = f[1].data.field(9)
	pos_z = f[1].data.field(10)
	return time,qsj1,qsj2,qsj3,qsj4,pos_x,pos_y,pos_z

def find_right_list(file_link,met):
	time,qsj1,qsj2,qsj3,qsj4,pos_x,pos_y,pos_z = open_fit(file_link)
	t = (time - met)**2
	t = np.array(t)
	index = np.where(t == np.min(t))
	#print('Closest MET (loc): ',time[index][0])
	qsj = np.array([qsj1[index][0],qsj2[index][0],qsj3[index][0],qsj4[index][0]])
	pos = np.array([pos_x[index][0],pos_y[index][0],pos_z[index][0]])
	return qsj,pos



def my_detectorplot(timestr):
	#print('Current UTC time: ', timestr)
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
	filename = filelist[0]
	#print('Retrieving info from:', filename)
	filelink = os.path.join(localdir,filename)
	met = get_met_from_utc(timestrisot)
	#print('Corresponding MET: ',met)
	qsj,pos = find_right_list(filelink,met)
	myGBM = GBM(qsj,pos*u.m,timestrisot)

	#seps=myGBM.get_separation(grb, BGO=False)
	#seps.sort("Detector")
	#separray=np.array([seps['Separation'][i] for i in range(12)])
	#mycondition=separray<=60
	#mycondition=mycondition.astype(int)
	#np.savetxt(resultdir+'contain_'+str(met)+'.txt',[mycondition],fmt='%i')
	fig = plt.figure(figsize=(15,15))
	ax = fig.add_subplot(111)
	map = Basemap(projection='moll', lat_0=0, lon_0=180,
                             resolution='l', area_thresh=1000.0, celestial=True, ax=ax)
	myGBM.detector_plot(radius = 10,lat_0 = 0,lon_0 = 90, show_bodies = True, BGO = False, map=map)
	#x,y=map(grb.ra.value,grb.dec.value)
	#label='  GW170817'
	#plt.text(x, y, label, fontsize=12)	

	#mysourcestr=["16h19m55.07s -15d38m24.8s"]	
	#mysource=SkyCoord(mysourcestr,frame = 'icrs')
	#x,y=map(mysource.ra.value,mysource.dec.value)
	#labels=['  Sco X-1']
	#for i in range(x.size):
	#	map.plot(x[i], y[i], color='b',marker='*',markersize=15)
	#	plt.text(x[i], y[i], labels[i],fontsize=12)	
	az1 = np.arange(0,360,30)
	zen1 = np.zeros(az1.size)+2
	azname = []
	for i in az1:
		azname.append(r'${\/%s\/^{\circ}}$'%str(i))
	x1,y1 = map(az1,zen1)
	for index,value in enumerate(az1):
		plt.text(x1[index],y1[index],azname[index],size = 20)
	_ = map.drawmeridians(np.arange(0, 360, 30),dashes=[1,0],color='#d9d6c3')
	_ = map.drawparallels(np.arange(-90, 90, 15),dashes=[1,0], labels=[1,0,0,1], color='#d9d6c3',size = 20)
	map.drawmapboundary(fill_color='#f6f5ec')
	plt.title(timestr,fontsize=25)
	plt.savefig(resultdir+'gbm_'+timestr.replace(':','_')+'.png')

#daystr='2017-03-24 '
#timestr=':00:00'
#hourstr=['00','01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
#timelist = ['2017-03-24 07:53:55.36','2017-03-24 07:57:15.36','2017-03-24 08:02:15.36']
#timelistarr=[' ']*len(hourstr)
#for i in range(len(hourstr)):
#	timelistarr[i]=daystr+hourstr[i]+timestr
met1=utc2met(['2016-06-07 09:16:08'])
met2=utc2met(['2016-06-07 09:17:48'])
#met_trig=utc2met(['2018-06-01 08:16:46.10'])
met=np.arange(met1[0],met2[0],5.0)
print(met.size)
timelist=met2utc(met)
#grb = SkyCoord("13h09m48.085s -23d22m53.343s",frame = 'icrs')

datadir = '/diska/Fermi_GBM_daily/data/'
topdir = './'
resultdir = topdir+'/results/'
if os.path.exists(resultdir)== False:
	os.makedirs(resultdir)
if __name__ == '__main__':
	p = Pool(80)
	p.map(my_detectorplot, timelist)
