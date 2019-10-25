# General analyses of GBM daily data
import matplotlib
matplotlib.use('Agg')
from astropy.io import fits
from astropy.time import Time
from astropy.table import Table
from astropy.coordinates import get_sun,get_body_barycentric,cartesian_to_spherical
from astropy.coordinates import SkyCoord, cartesian_to_spherical
from glob import glob
import time
import h5py
import pandas as pd
import numpy as np
import functools
from scipy.stats import poisson
from scipy.stats import norm
import os
import sys
from collections import OrderedDict
import astropy.units as u
from matplotlib import pyplot as plt
import matplotlib.colors as colors
from matplotlib import ticker
from multiprocessing import Pool
#supress rpy2 warnings for rpy2<3.0
import warnings
from rpy2.rinterface import RRuntimeWarning
warnings.filterwarnings("ignore", category=RRuntimeWarning)
#supress rpy2 warnings for rpy2>=3.0
#from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
#import logging
#rpy2_logger.setLevel(logging.ERROR) 
from rpy2.robjects import r
from rpy2.robjects import numpy2ri
r("library(baseline)")
numpy2ri.activate()
from personal_settings import *

DATABASEDIR = get_dailydatabasedir()
NaI=['n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb']
BGO = ['b0','b1']
Det = ['b0','b1','n0','n1','n2','n3','n4','n5','n6','n7','n8','n9','na','nb']
#data in firt and last two channels of BGO and NaI are not used
#ignore 0,1,2,125,126,127, notice 3-124
CH1 = 3
CH2 = 124

##################
# SOME FUNCTIONS #
##################

def set_ncore():
	Ncore = os.cpu_count()
	if Ncore < 10:
		use_ncore = Ncore - 1
	else:
		use_ncore = Ncore - 2
	return use_ncore

def timer(func):
	"""Print the runtime of the decorated function"""
	@functools.wraps(func)
	def wrapper_timer(*args,**kwargs):
		print(f"Running {func.__name__!r} for:",args[0],"...")
		start_time=time.perf_counter()
		value=func(*args,**kwargs)
		end_time=time.perf_counter()
		run_time=end_time-start_time
		print(f"Finished {func.__name__!r} for {args[0][0]} in {run_time:.4f} sec")
		return value
	return wrapper_timer

def utc2met(myUTCstring):
	UTC0=Time('2001-01-01',format='iso',scale='utc')
	myUTC=Time(myUTCstring,format='iso',scale='utc')
	datastart='2008-08-07 03:35:44.0' # valid data start 9 weeks after the mission starts
	datastartUTC=Time(datastart,format='iso',scale='utc')
	assert myUTC>=datastartUTC,'**** ERROR: One of the UTC TIME is not valid!!! ****: '+myUTCstring
	return myUTC.gps-UTC0.gps

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

###########################
# BEGIN class TIMEWINDOW #
###########################

class TIMEWINDOW:

	def __init__(self, winname, StartUTC, EndUTC, resultdir='./results'):
		self.winname = winname
		self.Startmet = utc2met([StartUTC])[0]
		self.Endmet = utc2met([EndUTC])[0]
		self.resultdir = resultdir+'/'+winname+'/'
		if os.path.exists(self.resultdir)== False:
			os.makedirs(self.resultdir)
		self.datadir = self.resultdir+'/data/'
		if os.path.exists(self.datadir)== False:
			os.makedirs(self.datadir)	
		hourlist = get_hourlist(StartUTC,EndUTC)
		if os.path.exists(self.datadir+'/data.h5')== False:
			f = h5py.File(self.datadir+'/data.h5',mode='w')
			for i in range(14):
				f.create_group(Det[i])
				timeforsave = np.array([])
				chforsave = np.array([])
				for hourstr in hourlist:
					year = hourstr[:4]
					yearshort = hourstr[2:4]
					month = hourstr[5:7]
					day = hourstr[8:10]
					hour = hourstr[11:13]+'z'
					thisdatadir = DATABASEDIR+'/'+year+'/'+month+'/'+day+'/'
					tbegin_met = utc2met(hourstr)
					tend_met=tbegin_met+3600.00
					ttefile=glob(thisdatadir+'glg_tte_'+Det[i]+'_'+yearshort+month+day+'_'+hour+'_*')
					filenum=len(ttefile)
					if  filenum==1:
						hdu=fits.open(ttefile[0])
						data=hdu['EVENTS'].data
						time=data.field(0)
						ch=data.field(1)
						validindex=(time>=tbegin_met) & (time<tend_met) & (time>=self.Startmet) & (time<=self.Endmet)
						time=time[validindex]
						ch=ch[validindex]
						if len(time)>1:
							ch_index = (ch>=CH1) & (ch<=CH2)
							time=time[ch_index]
							ch=ch[ch_index]
							if len(time)>1:
								timeforsave = np.concatenate([timeforsave, time])
								chforsave = np.int8(np.concatenate([chforsave, ch]))
				f['/'+Det[i]+'/time'] = timeforsave
				f['/'+Det[i]+'/ch'] = chforsave
			f.flush()
			f.close()
	
	def plot_rawlc(self, binwidth=0.064):
		if not os.path.exists(self.resultdir+'/raw_lc.png'):
			f = h5py.File(self.datadir+'/data.h5',mode='r')
			fig, axes = plt.subplots(7,2,figsize=(32, 20),
									sharex=True,sharey=False)
			for i in range(14):
				time = f['/'+Det[i]+'/time'][()]
				viewt1 = np.min(time)
				viewt2 = np.max(time)
				tbins = np.arange(viewt1,viewt2+binwidth,binwidth)
				histvalue, histbin = np.histogram(time,bins=tbins)
				plotrate = histvalue/binwidth
				plotrate = np.concatenate(([plotrate[0]],plotrate))
				axes[i//2,i%2].plot(histbin,plotrate,drawstyle='steps')
				axes[i//2,i%2].set_xlim([viewt1,viewt2])
				axes[i//2,i%2].tick_params(labelsize=25)
				axes[i//2,i%2].text(0.05,0.85,Det[i],fontsize=25,
									transform=axes[i//2,i%2].transAxes)
			fig.text(0.07, 0.5, 'Count rate (count/s)', ha='center',
						va='center',rotation='vertical',fontsize=30)
			fig.text(0.5, 0.05, 'Time (s)', ha='center',
								va='center',fontsize=30)		
			plt.savefig(self.resultdir+'/raw_lc.png')
			plt.close()
			f.close()

	def base(self,binwidth=0.064):
		f = h5py.File(self.datadir+'/data.h5',mode='r')
		for i in range(14):
			time = f['/'+Det[i]+'/time'][()]
			ch = f['/'+Det[i]+'/ch'][()]
			viewt1 = np.min(time)
			viewt2 = np.max(time)
			for chno in np.arange(CH1,CH2+1):
				time_selected = time[ch==chno]
				time_selected.sort()
				GTI0_t1 = time_selected[0]
				GTI0_t1 = time_selected[0]

# ***********************old************************

# https://en.wikipedia.org/wiki/Normal_distribution
def norm_pvalue(sigma):
	p = norm.cdf(sigma)-norm.cdf(-sigma)
	return p


def get_hourlist(StartUTC,EndinUTC):
	hourstrs=['00','01','02','03','04','05','06','07','08','09','10',\
	'11','12','13','14','15','16','17','18','19','20','21','22','23']
	t0tmp='2000-01-01'
	t1tmp='2000-01-02'
	oneday=Time(t1tmp)-Time(t0tmp)
	Startdate=StartUTC[:10]
	Endindate=EndinUTC[:10]
	Starthour=StartUTC[11:13]
	Endinhour=EndinUTC[11:13]
	starthourindex=hourstrs.index(Starthour)
	endinhourindex=hourstrs.index(Endinhour)
	Startday=Time(Startdate,format='iso',scale='utc')
	Endinday=Time(Endindate,format='iso',scale='utc')
	deltaday=int((Endinday-Startday).jd)
	if deltaday==0:
		deltahour=int(Endinhour)-int(Starthour)
		if deltahour<0:
			sys.exit('***ERROR: Check if StartUTC and EndinUTC are valid!')
		hourlist=[Startdate+' '+hourstrs[starthourindex+i]+':00:00'  for i in range(deltahour+1)]
	elif deltaday==1:
		hourlist=[Startdate+' '+hourstrs[starthourindex+i]+':00:00'  for i in range(24-starthourindex)]
		hourlist1=[Endindate+' '+hourstrs[i]+':00:00'  for i in range(endinhourindex+1)]
		hourlist.extend(hourlist1)
	elif deltaday>=2:
		hourlist=[Startdate+' '+hourstrs[starthourindex+i]+':00:00'  for i in range(24-starthourindex)]
		for i in range(deltaday-1):
			anotherdaystr=(Startday+oneday*(i+1)).iso
			hourlist2=[anotherdaystr[0:10]+' '+hourstrs[j]+':00:00' for j in range(24)]
			hourlist.extend(hourlist2)
		hourlist2=[Endindate+' '+hourstrs[i]+':00:00'  for i in range(endinhourindex+1)]
		hourlist.extend(hourlist2)
	else:
		sys.exit('***ERROR: Check if StartUTC and EndinUTC are valid!')
	return hourlist



def gen_ttedata(pars):
	# pars=[hourstr,ttehourdatadir,Startmet,Endinmet,ch1,ch2] for parellel
	# hourstr as in '2015-03-14 04:00:00'
	# ttehourdatadir in string
	# ch1 and ch2 as channel numbers in integer
	hourstr = pars[0]
	ttehourdatadir = pars[1]
	Startmet = pars[2]
	Endinmet = pars[3]
	ch1=pars[4]
	ch2=pars[5]
	year = hourstr[:4]
	yearshort = hourstr[2:4]
	month = hourstr[5:7]
	day = hourstr[8:10]
	hour = hourstr[11:13]+'z'
	datadir = databasedir+'/'+year+'/'+month+'/'+day+'/'
	tbegin_met = utc2met([hourstr])
	tbegin_met = tbegin_met[0]
	tend_met=tbegin_met+3600.00
	for i in range(12):
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
			sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		data=hdu['EVENTS'].data
		time=data.field(0)
		ch=data.field(1)
		GTI=hdu['GTI'].data
		tbegin=GTI[0][0]
		validindex=(time>=tbegin_met) & (time< tend_met) & (time>=Startmet) & (time<=Endinmet)
		time_corrected=time[validindex]
		ch_corrected=ch[validindex]
		# abandon invalid UTC time slice in cases
		# when given UTC time slice is very close to the GTI edges
		# or when the given UTC time slice is not in any GTI region
		if len(time_corrected)>1:
			ch_index=(ch_corrected>=ch1) & (ch_corrected<=ch2)
			time_save=time_corrected[ch_index]
			ch_save=ch_corrected[ch_index]
			if len(time_save)>1:
				df=pd.DataFrame(np.array([time_save,ch_save]).T,columns=['time','ch'])
				df.to_csv(ttehourdatadir+'/'+hourstr+'_'+NaI[i]+'_tte.csv',index=False)

# plot the raw lightcurve using the TTE data generated above
# AND generate GTI for later usages
def plot_rawlc_gen_GTIs(ch1,ch2,hourlist,ttehourdatadir,Startmet,Endinmet,StartUTC,EndinUTC,\
							lcbinwidth,GTIdir,rawlcdir,resultdir,trigtime_str=None):
	fig = plt.figure(figsize=(60, 30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		#find out energy range
		year=hourlist[0][:4]
		yearshort=hourlist[0][2:4]
		month=hourlist[0][5:7]
		day=hourlist[0][8:10]
		hour=hourlist[0][11:13]+'z'
		datadir=databasedir+'/'+year+'/'+month+'/'+day+'/'
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
			sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		ebound=hdu['EBOUNDS'].data
		emin=ebound.field(1)
		# generate the full TTE data and save for later usage
		df=pd.DataFrame(np.array([[],[]]).T,columns=['time','ch'])
		for hourstr in hourlist:
			if os.path.exists(ttehourdatadir+'/'+hourstr+'_'+NaI[i]+'_tte.csv')== True:
				df1=pd.read_csv(ttehourdatadir+'/'+hourstr+'_'+NaI[i]+'_tte.csv')
				df=pd.concat([df,df1])
		# check if the data during given UTC slice are valid for plotting
		if len(df)<1:
			sys.exit('No valid data during the given UTC slice! Plotting is not successful!')
		df.to_csv(ttehourdatadir+'/'+NaI[i]+'_tte.csv',index=False)
		# make GTI regions from raw light curves by determining
		# where the gap between neighboring photons is larger than 5 second
		timeseq=df['time'].get_values()
		GTI0_t1=df['time'].get_values()[0]
		GTI0_t2=df['time'].get_values()[-1]
		timeseq.sort()
		timeseq2=timeseq[1:]
		timeseq1=timeseq[:-1]
		deltime=timeseq2-timeseq1
		delindex=deltime>5
		if len(timeseq1[delindex])>=1:
			GTI_t1=np.array(np.append([GTI0_t1],timeseq2[delindex]))
			GTI_t2=np.array(np.append(timeseq1[delindex],[GTI0_t2]))
			dfGTI=pd.DataFrame(np.array([GTI_t1,GTI_t2]).T,columns=['t1','t2'])
			dfGTI.to_csv(GTIdir+'/'+NaI[i]+'_GTI.csv',index=False)
		else:
			dfGTI=pd.DataFrame(np.array([[GTI0_t1],[GTI0_t2]]).T,columns=['t1','t2'])
			dfGTI.to_csv(GTIdir+'/'+NaI[i]+'_GTI.csv',index=False)
		#plot raw light curves
		tbins=np.arange(GTI0_t1,GTI0_t2+lcbinwidth,lcbinwidth)
		histvalue, histbin =np.histogram(df['time'],bins=tbins)
		plottime=histbin[:-1]+lcbinwidth/2.0
		plotrate=histvalue/lcbinwidth
		df=pd.DataFrame(np.array([plottime,plotrate]).T,columns=['time','rate'])
		df.to_csv(rawlcdir+'/'+NaI[i]+'_raw_lc.csv',index=False)
		plotrate=np.concatenate(([plotrate[0]],plotrate))
		ax.plot(histbin,plotrate,linestyle='steps')
		plt.text(0.1,0.88,NaI[i],transform=ax.transAxes,fontsize=30)
		plt.text(0.8,0.88,str(round(emin[ch1],1))+'-'+str(round(emin[ch2+1],1))+' keV',transform=ax.transAxes,fontsize=30)
		ax.tick_params(labelsize=15,top=True,right=True)
		if trigtime_str:
			ax.axvline(utc2met([trigtime_str])[0],ymax=0.1,color='r',linewidth=3.0)
			if i==1:
				ax.set_title('Trigtime= '+trigtime_str,fontsize=30)
		if i==10 or i ==11: 
			ax.set_xlabel('Time (s)',fontsize=30,labelpad=20)
		if i%2==0: 
			ax.set_ylabel('Count rate (s$^{-1}$)',fontsize=30,labelpad=20)
		if i==0: 
			ax.set_title(StartUTC+' -- '+EndinUTC,fontsize=30)
		
		ax.set_xlim([Startmet, Endinmet])
	plt.savefig(resultdir+'raw_lc.png')
	plt.close()

#the function for subtracting the background in each channel using R baseline and determining poisson level
def baseline_in_channel(pars):
	ch=pars[0]
	sigma=pars[1]
	ttehourdatadir=pars[2]
	GTIdir=pars[3]
	lcbinwidth=pars[4]
	baseresultdir=pars[5]
	for i in range(12):
		df=pd.read_csv(ttehourdatadir+'/'+NaI[i]+'_tte.csv')
		chs=df['ch'].astype('int')
		time_selected=df['time'][chs==ch]
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		# evaluate baseline separately for each GTI
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			histvalue, histbin=np.histogram(time_selected,bins=tbins)
			#rate=histvalue/lcbinwidth
			r.assign('rrate',histvalue) # rate= count per bin
			r("y=matrix(rrate,nrow=1)")
			# set fillPeak_int as many as the duration of light curve
			fillPeak_int=str(int(histbin[-1]-histbin[0]))
			#r("rbase=baseline(y,lam = 6, hwi=50, it=10, int = 100, method='fillPeaks')")
			r("rbase=baseline(y,lam = 6, hwi=10, it=10, int ="+fillPeak_int+", method='fillPeaks')")
			r("bs=getBaseline(rbase)")
			r("cs=getCorrected(rbase)")
			bs=r('bs')[0]
			cs=r('cs')[0]
			# poissonlevel: lamb should be >=1.0 to avoid triggering false weak signals
			poissonlevel=np.array([poisson_k(max(lamb,1.0),sigma=sigma) for lamb in bs])
			df=pd.DataFrame(np.array([histvalue,bs,cs,poissonlevel]).T,columns=['rate','base','net','poisson'])
			df.to_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch)+'.csv',index=False)


def plot_raw_countmap(hourlist,ttehourdatadir,Startmet, Endinmet,GTIdir,\
				lcbinwidth,ch1,ch2,resultdir,trigtime_str=None):
	fig = plt.figure(figsize=(60, 30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		year=hourlist[0][:4]
		yearshort=hourlist[0][2:4]
		month=hourlist[0][5:7]
		day=hourlist[0][8:10]
		hour=hourlist[0][11:13]+'z'
		datadir=databasedir+'/'+year+'/'+month+'/'+day+'/'
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
				sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		ebound=hdu['EBOUNDS'].data
		emin=ebound.field(1)
		# read out the full TTE data and GTI regions
		df=pd.read_csv(ttehourdatadir+'/'+NaI[i]+'_tte.csv')
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			x = tbins
			y = emin[ch1:ch2+2]
			X, Y = np.meshgrid(x, y)
			C=np.array([np.histogram(df['time'][df['ch']==chvalue],bins=tbins)[0] \
								for chvalue in np.arange(ch1,ch2+1)])
			C[C<1]=1
			pcm = plt.pcolor(X, Y, C,norm=colors.LogNorm(vmin=1.0, vmax=C.max()),\
									cmap='rainbow')

			#plt.pcolormesh(X, Y, np.log10(C))
		if trigtime_str:
			ax.axvline(utc2met([trigtime_str])[0],ymax=0.1,color='r',linewidth=3.0)
		plt.title(NaI[i],loc='left')
		#if i==0 or i ==1: ax.set_title(StartUTC+' -- '+EndinUTC,fontsize=30)
		ax.set_xlabel('Time (s)')
		ax.set_xlim([Startmet, Endinmet])
		ax.set_yscale('log')
		ax.set_ylabel('Energy (KeV)')
		ax.set_ylim([emin[ch1], emin[ch2+1]])
		ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
		cbar=fig.colorbar(pcm, extend='max')
		#cbar = plt.colorbar()
		#cbar.ax.set_ylabel('log(count rate per pixel)')
		cbar.ax.set_ylabel('count per pixel')
	plt.savefig(resultdir+'raw_countmap.png')
	plt.close()


# plot the net count map with baseline subtracted 
def plot_net_countmap(hourlist,ttehourdatadir,baseresultdir,Startmet, Endinmet,GTIdir,\
		lcbinwidth,ch1,ch2,resultdir,trigtime_str=None):
	fig = plt.figure(figsize=(60, 30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		year=hourlist[0][:4]
		yearshort=hourlist[0][2:4]
		month=hourlist[0][5:7]
		day=hourlist[0][8:10]
		hour=hourlist[0][11:13]+'z'
		datadir=databasedir+'/'+year+'/'+month+'/'+day+'/'
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
				sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		ebound=hdu['EBOUNDS'].data
		emin=ebound.field(1)
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			x = tbins
			y = emin[ch1:ch2+2]
			X, Y = np.meshgrid(x, y)
			C=np.array([pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+\
				'_ch'+str(chvalue)+'.csv')['net'] for chvalue in np.arange(ch1,ch2+1)])	
			#C[C<0]=np.min(C[C>0])
			C[C<1]=1
			pcm = plt.pcolor(X, Y, C,norm=colors.LogNorm(vmin=1.0,vmax=C.max()),\
													cmap='rainbow')
			#plt.pcolormesh(X, Y, np.log10(C))
			#plt.clim(0, )
		if trigtime_str:
			ax.axvline(utc2met([trigtime_str])[0],ymax=0.1,color='r',linewidth=3.0)
		plt.title(NaI[i],loc='left')
		ax.set_xlabel('Time (s)')
		ax.set_xlim([Startmet, Endinmet])
		ax.set_yscale('log')
		ax.set_ylabel('Energy (KeV)')
		ax.set_ylim([emin[ch1], emin[ch2+1]])
		ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
		cbar = plt.colorbar(pcm, extend='max')
		cbar.ax.set_ylabel('count per pixel')
	plt.savefig(resultdir+'net_countmap_baseline_subtracted.png')
	plt.close()


def plot_channellc_with_baseline_and_poisson(pars):
	ch_index=pars[0]
	sigma=pars[1]
	trigtime_str=pars[2]
	ttehourdatadir=pars[3]
	GTIdir=pars[4]
	lcbinwidth=pars[5]
	baseresultdir=pars[6]
	StartUTC=pars[7]
	EndinUTC=pars[8]
	Startmet=pars[9]
	Endinmet=pars[10]
	channellcdir=pars[11]
	fig = plt.figure(figsize=(60, 30))
	#fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(60,30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			plottime=tbins[:-1]+lcbinwidth/2.0
			df=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch_index)+'.csv')
			plotrate=df['base'].get_values()
			ax.plot(plottime,plotrate,linestyle='--',lw=4.0,color='tab:orange')
			plotpoisson=df['poisson'].get_values()
			ax.plot(plottime,plotpoisson,linestyle='--',lw=4.0,color='tab:red')
			plotrate=df['rate'].get_values()
			plotrate=np.concatenate(([plotrate[0]],plotrate))
			ax.plot(tbins,plotrate,linestyle='steps',color='tab:blue')
		plt.text(0.1,0.88,NaI[i],transform=ax.transAxes,fontsize=30)
		ax.tick_params(labelsize=15,top=True,right=True)
		ax.set_xlim([Startmet, Endinmet])
	plt.savefig(channellcdir+'lc_'+str(ch_index)+'.png')
	plt.close()

#plot raw light curve showing baseline 
def plot_rawlc_show_baseline(ch1,ch2,hourlist,Startmet,Endinmet,StartUTC,EndinUTC,\
							lcbinwidth,GTIdir,baseresultdir,resultdir,trigtime_str=None):
	fig = plt.figure(figsize=(60, 30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		#find out energy range
		year=hourlist[0][:4]
		yearshort=hourlist[0][2:4]
		month=hourlist[0][5:7]
		day=hourlist[0][8:10]
		hour=hourlist[0][11:13]+'z'
		datadir=databasedir+'/'+year+'/'+month+'/'+day+'/'
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
			sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		ebound=hdu['EBOUNDS'].data
		emin=ebound.field(1)
		# plot summed light curves
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			df=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch1)+'.csv')
			for ch_tmp in np.arange(ch1+1,ch2+1):
				df_tmp=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch_tmp)+'.csv')
				df=df+df_tmp
			plotrate=df['rate'].get_values()/lcbinwidth
			plotrate=np.concatenate(([plotrate[0]],plotrate))
			ax.plot(tbins,plotrate,linestyle='steps',lw=3.0,color='tab:blue')
			plotrate=df['base'].get_values()/lcbinwidth
			plottime=tbins[:-1]+lcbinwidth/2.0
			ax.plot(plottime,plotrate,linestyle='--',lw=4.0,color='tab:orange')
		plt.text(0.1,0.88,NaI[i],transform=ax.transAxes,fontsize=30)
		plt.text(0.8,0.88,str(round(emin[ch1],1))+'-'+str(round(emin[ch2],1))+' keV',transform=ax.transAxes,fontsize=30)
		ax.tick_params(labelsize=15,top=True,right=True)
		if trigtime_str:
			ax.axvline(utc2met([trigtime_str])[0],ymax=0.1,color='r',linewidth=3.0)
			if i==1:
				ax.set_title('Trigtime= '+trigtime_str,fontsize=30)
		if i==10 or i ==11:
			ax.set_xlabel('Time (s)',fontsize=30,labelpad=20)
		if i%2==0:
			ax.set_ylabel('Count rate (s$^{-1}$)',fontsize=30,labelpad=20)
		if i==0:
			ax.set_title(StartUTC+' -- '+EndinUTC,fontsize=30)
		ax.set_xlim([Startmet, Endinmet])
	plt.savefig(resultdir+'raw_lc_show_base.png')
	plt.close()
	
#plot net light curve with baseline subtracted 
def plot_netlc(ch1,ch2,hourlist,Startmet,Endinmet,StartUTC,EndinUTC,\
							lcbinwidth,GTIdir,baseresultdir,resultdir,trigtime_str=None):
	plotymax=0.0
	# load net light curves and determine ymax
	for i in range(12):
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			df=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch1)+'.csv')
			for ch_tmp in np.arange(ch1+1,ch2+1):
				df_tmp=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch_tmp)+'.csv')
				df=df+df_tmp
			plotrate=df['net'].get_values()/lcbinwidth
			ymax=plotrate.max()
			if plotymax<ymax: 
				plotymax=ymax	
	# load and plot net light curves with set ymax	
	fig = plt.figure(figsize=(60, 30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		#find out energy range
		year=hourlist[0][:4]
		yearshort=hourlist[0][2:4]
		month=hourlist[0][5:7]
		day=hourlist[0][8:10]
		hour=hourlist[0][11:13]+'z'
		datadir=databasedir+'/'+year+'/'+month+'/'+day+'/'
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
			sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		ebound=hdu['EBOUNDS'].data
		emin=ebound.field(1)
		# plot net light curves
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			df=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch1)+'.csv')
			for ch_tmp in np.arange(ch1+1,ch2+1):
				df_tmp=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch_tmp)+'.csv')
				df=df+df_tmp
			plotrate=df['net'].get_values()/lcbinwidth
			plotrate=np.concatenate(([plotrate[0]],plotrate))
			ax.plot(tbins,plotrate,linestyle='steps',lw=3.0,color='tab:blue')
		plt.text(0.1,0.88,NaI[i],transform=ax.transAxes,fontsize=30)
		plt.text(0.8,0.88,str(round(emin[ch1],1))+'-'+str(round(emin[ch2],1))+' keV',transform=ax.transAxes,fontsize=30)
		ax.tick_params(labelsize=15,top=True,right=True)
		if trigtime_str:
			ax.axvline(utc2met([trigtime_str])[0],ymax=0.1,color='r',linewidth=3.0)
			if i==1:
				ax.set_title('Trigtime= '+trigtime_str,fontsize=30)
		if i==10 or i ==11:
			ax.set_xlabel('Time (s)',fontsize=30,labelpad=20)
		if i%2==0:
			ax.set_ylabel('Count rate (s$^{-1}$)',fontsize=30,labelpad=20)
		if i==0:
			ax.set_title(StartUTC+' -- '+EndinUTC,fontsize=30)
		ax.set_xlim([Startmet, Endinmet])
		ax.set_ylim([0,plotymax])
	plt.savefig(resultdir+'net_lc_backfree.png')
	plt.close()

# plot the baseline subtracted 2D count map only showing pixels over poisson level
def plot_net_countmap_over_poisson_level(hourlist,ttehourdatadir,baseresultdir,\
		Startmet, Endinmet,GTIdir,lcbinwidth,ch1,ch2,resultdir,trigtime_str=None):
	fig = plt.figure(figsize=(60, 30))
	for i in range(12):
		ax = plt.subplot2grid((6,2),(i//2,i%2))
		year=hourlist[0][:4]
		yearshort=hourlist[0][2:4]
		month=hourlist[0][5:7]
		day=hourlist[0][8:10]
		hour=hourlist[0][11:13]+'z'
		datadir=databasedir+'/'+year+'/'+month+'/'+day+'/'
		ttefile=glob(datadir+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		filenum=len(ttefile)
		if  filenum!=1:
				sys.exit('wrong file:'+'glg_tte_'+NaI[i]+'_'+yearshort+month+day+'_'+hour+'_*')
		hdu=fits.open(ttefile[0])
		ebound=hdu['EBOUNDS'].data
		emin=ebound.field(1)
		dfGTI=pd.read_csv(GTIdir+'/'+NaI[i]+'_GTI.csv')
		nGTI=len(dfGTI)
		for ii in range(nGTI):
			tbins=np.arange(dfGTI['t1'][ii],dfGTI['t2'][ii]+lcbinwidth,lcbinwidth)
			x = tbins
			y = emin[ch1:ch2+2]
			X, Y = np.meshgrid(x, y)
			#C=np.array([pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+\
			#	'_ch'+str(chvalue)+'.csv')['net'] for chvalue in np.arange(ch1,ch2+1)])
			df=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(ch1)+'.csv')
			net_tmp=df['net'].get_values()
			rate_tmp=df['rate'].get_values()
			poisson_tmp=df['poisson'].get_values()
			net_tmp[rate_tmp <= poisson_tmp]=1.0
			C=net_tmp
			for chvalue in np.arange(ch1+1,ch2+1):
				df=pd.read_csv(baseresultdir+'/'+NaI[i]+'/GTI_'+str(ii)+'_ch'+str(chvalue)+'.csv')
				net_tmp=df['net'].get_values()
				rate_tmp=df['rate'].get_values()
				poisson_tmp=df['poisson'].get_values()
				net_tmp[rate_tmp <= poisson_tmp]=1.0
				C=np.vstack((C,net_tmp))
			pcm = plt.pcolor(X, Y, C,norm=colors.LogNorm(vmin=1.0,vmax=C.max()),\
													cmap='rainbow')
		if trigtime_str:
			ax.axvline(utc2met([trigtime_str])[0],color='r',linestyle='--',linewidth=2.0)
		plt.title(NaI[i],loc='left')
		ax.set_xlabel('Time (s)')
		ax.set_xlim([Startmet, Endinmet])
		ax.set_yscale('log')
		ax.set_ylabel('Energy (KeV)')
		ax.set_ylim([emin[ch1], emin[ch2+1]])
		ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.0f'))
		cbar = plt.colorbar(pcm, extend='max')
		cbar.ax.set_ylabel('count per pixel')
	plt.savefig(resultdir+'net_countmap_baseline_subtracted_over_poisson_level.png')
	plt.close()
