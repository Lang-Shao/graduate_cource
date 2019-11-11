# General analyses of GBM daily data
import matplotlib
matplotlib.use('Agg')
import os
import sys
import operator
import time
import h5py
import pandas as pd
import numpy as np
import functools
import pysnooper
#@pysnooper.snoop('./log.txt')
from astropy.io import fits
from astropy.time import Time
from astropy.stats import sigma_clip, mad_std
import astropy.units as u
from glob import glob
from scipy import stats
from matplotlib import pyplot as plt
from matplotlib import ticker
import matplotlib.colors as colors
from multiprocessing import Pool
# -supress rpy2 warnings
import rpy2
rpy2_ver = rpy2.__version__
if rpy2_ver[0] == '2':
	import warnings
	from rpy2.rinterface import RRuntimeWarning
	warnings.filterwarnings("ignore", category=RRuntimeWarning)
else:
	from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
	import logging
	rpy2_logger.setLevel(logging.ERROR)
# ---------------------
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

# https://en.wikipedia.org/wiki/Normal_distribution
# https://en.wikipedia.org/wiki/Poisson_distribution
# cdfprob = 0.997300203937 # 3 sigma
# cdfprob = 0.954499736104 # 2 sigma
# cdfprob = 0.682689492137 # 1 sigma
def norm_pvalue(sigma=3.0):
	p = stats.norm.cdf(sigma)-stats.norm.cdf(-sigma)
	return p


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

###########################
# BEGIN class TIMEWINDOW #
###########################


class TIMEWINDOW:
	def __init__(self, winname, StartUTC, EndUTC, binwidth=0.64, resultdir='./results'):
		self.winname = winname
		self.Startmet = utc2met([StartUTC])[0]
		self.Endmet = utc2met([EndUTC])[0]
		self.resultdir = resultdir+'/'+winname+'/'
		if not os.path.exists(self.resultdir):
			os.makedirs(self.resultdir)
		self.datadir = self.resultdir+'/data/'
		if not os.path.exists(self.datadir):
			os.makedirs(self.datadir)	
		self.hourlist = get_hourlist(StartUTC,EndUTC)
		if not os.path.exists(self.datadir+'/base.h5'):
			base_f = h5py.File(self.datadir+'/base.h5',mode='w')
			fig, axes = plt.subplots(7,2,figsize=(32, 20),
									sharex=True,sharey=False)
			for i in range(14):
				timedata = np.array([])
				for hourstr in self.hourlist:
					year = hourstr[:4]
					yearshort = hourstr[2:4]
					month = hourstr[5:7]
					day = hourstr[8:10]
					hour = hourstr[11:13]+'z'
					thisdatadir = DATABASEDIR+'/'+year+'/'+month+'/'+day+'/'
					hourbegin_met = utc2met(hourstr)
					hourend_met=hourbegin_met+3600.00
					ttefile=glob(thisdatadir+'glg_tte_'+Det[i]+'_'+yearshort+month+day+'_'+hour+'_*')
					filenum=len(ttefile)
					if  filenum==1:
						hdu=fits.open(ttefile[0])
						t=hdu['EVENTS'].data.field(0)
						ch=hdu['EVENTS'].data.field(1)
						validindex=(t>=hourbegin_met) & (t<hourend_met) & (t>=self.Startmet) & (t<=self.Endmet)
						t=t[validindex]
						ch=ch[validindex]
						if len(t)>1:
							ch_index = (ch>=CH1) & (ch<=CH2)
							t=t[ch_index]
							if len(t)>1:
								timedata = np.concatenate([timedata, t])
				if len(timedata) > 1000: # considered enough data for being a valid timewindow
					GTI0_t1 = timedata[0]
					GTI0_t2 = timedata[-1]
					# A gap is considered existing where neighboring photons separate for larger than 5 second
					gapindex = (timedata[1:] - timedata[:-1]) > 5
					if np.sum(gapindex) >= 1:
						GTI_t1 = np.array(np.append([GTI0_t1],timedata[1:][gapindex]))
						GTI_t2 = np.array(np.append(timedata[:-1][gapindex],[GTI0_t2]))
						GTI_array = np.array([GTI_t1,GTI_t2])
					else:
						GTI_array = np.array([[GTI0_t1],[GTI0_t2]])
					base_f['/GTI/'+Det[i]] = GTI_array
					nGTI = len(GTI_array[0])
					for ii in range(nGTI):
						tbins = np.arange(GTI_array[0][ii], GTI_array[1][ii]+binwidth, binwidth)
						histvalue, histbin=np.histogram(timedata,bins=tbins)
						rate = histvalue/binwidth
						r.assign('rrate',rate) 
						r("y=matrix(rrate,nrow=1)")
						fillPeak_hwi = str(max(int(5/binwidth),1))
						fillPeak_int = str(int(len(rate)/10))
						r("rbase=baseline(y,lam=6,hwi="+fillPeak_hwi
							+",it=10,int="+fillPeak_int+",method='fillPeaks')")
						r("bs=getBaseline(rbase)")
						r("cs=getCorrected(rbase)")
						bs = np.array(r('bs'))[0]
						cs = np.array(r('cs'))[0]
						# correct negative base to 0 and recover the net value to original rate
						corrections_index = (bs < 0)
						bs[corrections_index] = 0
						cs[corrections_index] = rate[corrections_index]
						base_f['/'+Det[i]+'/GTI'+str(ii)] = np.array([rate,bs,cs])
					#plot raw lc
					tbins = np.arange(GTI0_t1,GTI0_t2+binwidth,binwidth)
					histvalue, histbin = np.histogram(timedata,bins=tbins)
					plotrate = histvalue/binwidth
					plotrate = np.concatenate(([plotrate[0]],plotrate))
					axes[i//2,i%2].plot(histbin,plotrate,drawstyle='steps')
					if len(GTI_array[0]) > 1:
						for value in np.concatenate((GTI_array[0][1:],GTI_array[1][:-1])):
							axes[i//2,i%2].axvline(value,ymax=0.05,color='r',linewidth=3.0)
					axes[i//2,i%2].set_xlim([GTI0_t1,GTI0_t2])
					axes[i//2,i%2].set_ylim([0,axes[i//2,i%2].get_ylim()[1]])
					axes[i//2,i%2].tick_params(labelsize=25)
					axes[i//2,i%2].text(0.05,0.85,Det[i],fontsize=25,
										transform=axes[i//2,i%2].transAxes)
			fig.text(0.07, 0.5, 'Count rate (count/s)', ha='center',
						va='center',rotation='vertical',fontsize=30)
			fig.text(0.5, 0.05, 'MET Time (s)', ha='center',
								va='center',fontsize=30)		
			plt.savefig(self.resultdir+'/raw_lc.png')
			base_f.attrs["binwidth"] = 	str(binwidth)	
			base_f.flush()
			base_f.close()

	def plot_base(self): # only necessary for inspection purpose
		if not os.path.exists(self.resultdir+'/base.png'):
			base_f = h5py.File(self.datadir+'/base.h5',mode='r')
			binwidth = np.float(base_f.attrs['binwidth'])
			fig, axes = plt.subplots(7,2,figsize=(32, 20),
									sharex=True,sharey=False)
			for i in range(14):
				if '/GTI/'+Det[i] in base_f: # data exist for this Det
					GTI_array = base_f['/GTI/'+Det[i]][()]
					nGTI = len(GTI_array[0])
					for ii in range(nGTI):
						rate, bs, cs = base_f['/'+Det[i]+'/GTI'+str(ii)][()]			
						tbins = np.arange(GTI_array[0][ii], GTI_array[1][ii]+binwidth, binwidth)
						plotrate = np.concatenate(([rate[0]],rate))
						plotbs = np.concatenate(([bs[0]],bs))
						axes[i//2,i%2].plot(tbins,plotrate,drawstyle='steps',color='C0')
						axes[i//2,i%2].plot(tbins,plotbs,drawstyle='steps',color='C3')
					axes[i//2,i%2].set_xlim([GTI_array[0][0],GTI_array[1][-1]])
					axes[i//2,i%2].set_ylim([0,axes[i//2,i%2].get_ylim()[1]])
					axes[i//2,i%2].tick_params(labelsize=25)
					axes[i//2,i%2].text(0.05,0.85,Det[i],fontsize=25,
										transform=axes[i//2,i%2].transAxes)
			fig.text(0.07, 0.5, 'Count rate (count/s)', ha='center',
						va='center',rotation='vertical',fontsize=30)
			fig.text(0.5, 0.05, 'MET Time (s)', ha='center',
								va='center',fontsize=30)		
			plt.savefig(self.resultdir+'/base.png')
			plt.close()
			base_f.close()

	def plot_netlc(self):
		if not os.path.exists(self.resultdir+'/netlc.png'):
			base_f = h5py.File(self.datadir+'/base.h5',mode='r')
			binwidth = np.float(base_f.attrs['binwidth'])
			fig, axes = plt.subplots(7,2,figsize=(32, 20),
									sharex=True,sharey=False)
			plotBGOmax=0.0
			plotNaImax=0.0
			for i in range(14):
				if '/GTI/'+Det[i] in base_f: # data exist for this Det
					GTI_array = base_f['/GTI/'+Det[i]][()]
					nGTI = len(GTI_array[0])
					for ii in range(nGTI):
						_, _, net = base_f['/'+Det[i]+'/GTI'+str(ii)][()]		
						tbins = np.arange(GTI_array[0][ii], GTI_array[1][ii]+binwidth, binwidth)
						net = np.concatenate(([net[0]],net))
						axes[i//2,i%2].plot(tbins,net,drawstyle='steps',color='C0')
					if i <=1:
						BGOmax = axes[i//2,i%2].get_ylim()[1]
						if plotBGOmax < BGOmax:
							plotBGOmax = BGOmax
					else:
						NaImax = axes[i//2,i%2].get_ylim()[1]
						if plotNaImax < NaImax:
							plotNaImax = NaImax
					axes[i//2,i%2].set_xlim([GTI_array[0][0],GTI_array[1][-1]])
					axes[i//2,i%2].tick_params(labelsize=25)
					axes[i//2,i%2].text(0.05,0.85,Det[i],fontsize=25,
										transform=axes[i//2,i%2].transAxes)
			for i in range(14):
				if i<=1:
					axes[i//2,i%2].set_ylim([-0.01,plotBGOmax])
				else:
					axes[i//2,i%2].set_ylim([-0.01,plotNaImax])
			fig.text(0.07, 0.5, 'Count rate (count/s)', ha='center',
						va='center',rotation='vertical',fontsize=30)
			fig.text(0.5, 0.05, 'MET Time (s)', ha='center',
								va='center',fontsize=30)		
			plt.savefig(self.resultdir+'/netlc.png')
			plt.close()
			base_f.close()

	def check_netlc_gaussian_distribution(self,sigma=3):
		if not os.path.exists(self.resultdir+'/netlc_gaussian_distribution.png'):
			base_f = h5py.File(self.datadir+'/base.h5',mode='r')
			binwidth = np.float(base_f.attrs['binwidth'])
			fig, axes = plt.subplots(7,2,figsize=(32, 20),
									sharex=False,sharey=False)
			Y = stats.norm(loc=0,scale=1)
			gaussian_level = Y.interval(norm_pvalue(sigma))
			for i in range(14):
				if '/GTI/'+Det[i] in base_f: # data exist for this Det
					GTI_array = base_f['/GTI/'+Det[i]][()]
					nGTI = len(GTI_array[0])
					net = np.concatenate([base_f['/'+Det[i]+'/GTI'+str(ii)][()][2] for ii in range(nGTI)])
					mask = sigma_clip(net,sigma=5,maxiters=5,stdfunc=mad_std).mask
					myfilter = list(map(operator.not_, mask))
					net_median_part = net[myfilter]
					loc,scale = stats.norm.fit(net_median_part)
					bins = np.arange((net.min()-loc)/scale,(net.max()-loc)/scale,
						(net_median_part.max()-net_median_part.min()-loc)/scale/25)
					histvalue, histbin = np.histogram((net-loc)/scale,bins=bins)
					histvalue = np.concatenate(([histvalue[0]],histvalue))
					axes[i//2,i%2].fill_between(histbin,histvalue,step='pre',
													label='SNR')
					x = np.linspace((net_median_part.min()-loc)/scale,
									(net_median_part.max()-loc)/scale,
									num=100)
					axes[i//2,i%2].plot(x,Y.pdf(x)*net.size*(bins[1]-bins[0]),
								label='Gaussian Distribution',
								linestyle='--',lw=3.0,color='tab:orange')
					axes[i//2,i%2].tick_params(labelsize=25)
					axes[i//2,i%2].text(0.5,0.8,Det[i],fontsize=25,
									transform=axes[i//2,i%2].transAxes)
					axes[i//2,i%2].axvline(gaussian_level[0],ls='--',lw=2,
								color='green',label=str(sigma)+'$\sigma$ level')
					axes[i//2,i%2].axvline(gaussian_level[1],ls='--',lw=2,
								color='green')
					axes[i//2,i%2].set_xlim([-5,axes[i//2,i%2].get_xlim()[1]])
					if i == 1:
						axes[i//2,i%2].legend(fontsize=20)
			fig.text(0.07, 0.5, 'Numbers', ha='center', va='center',
									rotation='vertical',fontsize=30)
			fig.text(0.5, 0.05, 'Signal-to-Noise Ratio (SNR)',
						ha='center', va='center',fontsize=30)		
			plt.savefig(self.resultdir+'/netlc_gaussian_distribution.png')
			plt.close()
			base_f.close()

	# two groups of dets as in BGOs and NaIs
	def plot_combined_snr(self,binwidth=0.64,sigma=3.0):
		if not os.path.exists(self.resultdir+'/combined_snr.png'):
			fig, axes = plt.subplots(2,2,figsize=(20, 12),
								gridspec_kw={'wspace': 0.3},sharex=False,sharey=False)
			Y = stats.norm(loc=0,scale=1)
			gaussian_level = Y.interval(norm_pvalue(sigma))
			for plotgroupid, dets_onegroup in enumerate([BGO,NaI]):
				timedata_onegroup = []
				GTI_onegroup = []
				for det in dets_onegroup:
					timedata_onedet = np.array([])					
					for hourstr in self.hourlist:
						year = hourstr[:4]
						yearshort = hourstr[2:4]
						month = hourstr[5:7]
						day = hourstr[8:10]
						hour = hourstr[11:13]+'z'
						thisdatadir = DATABASEDIR+'/'+year+'/'+month+'/'+day+'/'
						hourbegin_met = utc2met(hourstr)
						hourend_met=hourbegin_met+3600.00
						ttefile=glob(thisdatadir+'glg_tte_'+det+'_'+yearshort+month+day+'_'+hour+'_*')
						filenum=len(ttefile)
						if  filenum==1:
							hdu=fits.open(ttefile[0])
							t=hdu['EVENTS'].data.field(0)
							ch=hdu['EVENTS'].data.field(1)
							validindex=(t>=hourbegin_met) & (t<hourend_met) & (t>=self.Startmet) & (t<=self.Endmet)
							t=t[validindex]
							ch=ch[validindex]
							if len(t)>1:
								ch_index = (ch>=CH1) & (ch<=CH2)
								t=t[ch_index]
								if len(t)>1:
									timedata_onedet = np.concatenate([timedata_onedet, t])
					if len(timedata_onedet) > 1000: # considered enough data for being a valid timewindow
						GTI0_t1 = timedata_onedet[0]
						GTI0_t2 = timedata_onedet[-1]
						# A gap is considered existing where neighboring photons separate for larger than 5 second
						gapindex = (timedata_onedet[1:] - timedata_onedet[:-1]) > 5
						if np.sum(gapindex) >= 1:
							GTI_t1 = np.array(np.append([GTI0_t1],timedata_onedet[1:][gapindex]))
							GTI_t2 = np.array(np.append(timedata_onedet[:-1][gapindex],[GTI0_t2]))
							GTI_onedet = np.array([GTI_t1,GTI_t2])
						else:
							GTI_onedet = np.array([[GTI0_t1],[GTI0_t2]])
						timedata_onegroup.append(timedata_onedet)
						GTI_onegroup.append(GTI_onedet)
				nDet = len(timedata_onegroup) # number of valid dets in this group
				optimalGTI_onegroup = GTI_onegroup[0]
				for i in range(1,len(GTI_onegroup)):
					assert optimalGTI_onegroup.shape == GTI_onegroup[i].shape, "wrong GTI shape for:"+dets_onegroup[i]
					for GTIid in range(len(optimalGTI_onegroup[0])):
						optimalGTI_onegroup[0][GTIid] = max(optimalGTI_onegroup[0][GTIid],
																GTI_onegroup[i][0][GTIid])
						optimalGTI_onegroup[1][GTIid] = min(optimalGTI_onegroup[1][GTIid],
																GTI_onegroup[i][1][GTIid])
				net_onegroup = []
				nGTI = len(optimalGTI_onegroup[0])
				for timedata in timedata_onegroup:
					net_onedet = []				
					for GTIid in range(nGTI):
						tbins = np.arange(optimalGTI_onegroup[0][GTIid], 
							optimalGTI_onegroup[1][GTIid]+binwidth, binwidth)
						histvalue, histbin=np.histogram(timedata,bins=tbins)
						rate = histvalue/binwidth
						r.assign('rrate',rate) 
						r("y=matrix(rrate,nrow=1)")
						fillPeak_hwi = str(max(int(5/binwidth),1))
						fillPeak_int = str(int(len(rate)/10))
						r("rbase=baseline(y,lam=6,hwi="+fillPeak_hwi
							+",it=10,int="+fillPeak_int+",method='fillPeaks')")
						r("bs=getBaseline(rbase)")
						r("cs=getCorrected(rbase)")
						bs = np.array(r('bs'))[0]
						cs = np.array(r('cs'))[0]
						# correct negative base to 0 and recover the net value to original rate
						corrections_index = (bs < 0)
						bs[corrections_index] = 0
						cs[corrections_index] = rate[corrections_index]
						net_onedet.append(cs)
					net_onegroup.append(net_onedet)
				combined_net_GTIs = [
						np.sum(np.array([net_onegroup[detid][GTIid] for detid in range(nDet)]),axis=0)
													 for GTIid in range(nGTI) ]
				combined_net = np.concatenate(combined_net_GTIs)
				mask = sigma_clip(combined_net,sigma=5,maxiters=5,stdfunc=mad_std).mask
				myfilter = list(map(operator.not_, mask))
				combined_net_median_part = combined_net[myfilter]
				loc,scale = stats.norm.fit(combined_net_median_part)
				for GTIid in range(nGTI):
					tbins = np.arange(optimalGTI_onegroup[0][GTIid], 
							optimalGTI_onegroup[1][GTIid]+binwidth, binwidth)
					snr = (combined_net_GTIs[GTIid] - loc) / scale
					snr= np.concatenate(([snr[0]],snr))
					axes[plotgroupid,1].plot(tbins,snr,drawstyle='steps',color='C0')
				snr = (combined_net - loc)/scale
				bins = np.arange(snr.min(), snr.max(), 0.2)
				histvalue, histbin = np.histogram(snr,bins=bins)
				histvalue = np.concatenate(([histvalue[0]],histvalue))
				axes[plotgroupid,0].fill_between(histbin,histvalue,step='pre',
												label='Detectors-combined')
				x = np.arange(-5,5,0.1)
				axes[plotgroupid,0].plot(x,Y.pdf(x)*snr.size*(bins[1]-bins[0]),
							label='Gaussian Distribution',
							linestyle='--',lw=3.0,color='tab:orange')
				axes[plotgroupid,0].tick_params(labelsize=25)
				axes[plotgroupid,0].set_xlim([-5,10])
				axes[plotgroupid,0].axvline(gaussian_level[0],ls='--',lw=2,
							color='green',label=str(sigma)+'$\sigma$ level')
				axes[plotgroupid,0].axvline(gaussian_level[1],ls='--',lw=2,
							color='green')
				axes[plotgroupid,1].tick_params(labelsize=15)
				axes[plotgroupid,1].set_xlim([self.Startmet,self.Endmet])
				axes[plotgroupid,1].set_ylim([-0.01,axes[plotgroupid,1].get_ylim()[1]])
			for i in range(2):
				axes[0,i].text(0.1,0.8,'BGOs',fontsize=25,
									transform=axes[0,i].transAxes)
				axes[1,i].text(0.1,0.8,'NaIs',fontsize=25,
									transform=axes[1,i].transAxes)
			axes[0,0].legend(fontsize=15)
			fig.text(0.52, 0.5, 'Signal-to-Noise Ratio (SNR)', ha='center',
						va='center',rotation='vertical',fontsize=25)
			fig.text(0.75, 0.05, 'MET Time (s)', ha='center',
								va='center',fontsize=25)
			fig.text(0.07, 0.5, 'Numbers', ha='center', va='center',
									rotation='vertical',fontsize=25)
			fig.text(0.3, 0.05, 'Signal-to-Noise Ratio (SNR)',
						ha='center', va='center',fontsize=25)
			plt.savefig(self.resultdir+'/combined_snr.png')
			plt.close()


	def plot_netlc_snr(self,sigma=3):
		if not os.path.exists(self.resultdir+'/netlc_snr.png'):
			base_f = h5py.File(self.datadir+'/base.h5',mode='r')
			binwidth = np.float(base_f.attrs['binwidth'])
			fig, axes = plt.subplots(7,2,figsize=(32, 20),
									sharex=False,sharey=False)
			plotBGOmax=0.0
			plotNaImax=0.0
			for i in range(14):
				if '/GTI/'+Det[i] in base_f: # data exist for this Det
					GTI_array = base_f['/GTI/'+Det[i]][()]
					nGTI = len(GTI_array[0])
					net = np.concatenate([base_f['/'+Det[i]+'/GTI'+str(ii)][()][2] for ii in range(nGTI)])
					mask = sigma_clip(net,sigma=5,maxiters=5,stdfunc=mad_std).mask
					myfilter = list(map(operator.not_, mask))
					net_median_part = net[myfilter]
					loc,scale = stats.norm.fit(net_median_part)
					for ii in range(nGTI):
						_, _, net = base_f['/'+Det[i]+'/GTI'+str(ii)][()]			
						tbins = np.arange(GTI_array[0][ii], GTI_array[1][ii]+binwidth, binwidth)
						snr = (net-loc)/scale
						snr = np.concatenate(([snr[0]],snr))
						axes[i//2,i%2].plot(tbins,snr,drawstyle='steps',color='C0')
					if i <=1:
						BGOmax = axes[i//2,i%2].get_ylim()[1]
						if plotBGOmax < BGOmax:
							plotBGOmax = BGOmax
					else:
						NaImax = axes[i//2,i%2].get_ylim()[1]
						if plotNaImax < NaImax:
							plotNaImax = NaImax
					axes[i//2,i%2].set_xlim([GTI_array[0][0],GTI_array[1][-1]])
					axes[i//2,i%2].tick_params(labelsize=25)
					axes[i//2,i%2].text(0.05,0.85,Det[i],fontsize=25,
										transform=axes[i//2,i%2].transAxes)
					axes[i//2,i%2].axhline(sigma,
						ls='--',lw=3,color='orange',
						label=str(sigma)+'$\sigma$ level of gaussian background')
			for i in range(14):
				if i<=1:
					#axes[i//2,i%2].set_ylim([0,plotBGOmax])
					axes[i//2,i%2].set_ylim([0,20])
				else:
					#axes[i//2,i%2].set_ylim([0,plotNaImax])
					axes[i//2,i%2].set_ylim([0,20])
			axes[0,1].legend(fontsize=20)
			fig.text(0.07, 0.5, 'Signal-to-Noise Ratio (SNR)', ha='center',
					va='center',rotation='vertical',fontsize=30)
			fig.text(0.5, 0.05, 'MET Time (s)', ha='center',
							va='center',fontsize=30)	
			plt.savefig(self.resultdir+'/netlc_snr.png')
			plt.close()
			base_f.close()

	def plot_max_snr_versus_binsize(self):
		if not os.path.exists(self.resultdir+'/max_snr_versus_binsize.png'):
			fig, axes = plt.subplots(2,1,figsize=(10, 12),
								gridspec_kw={'wspace': 0.3},sharex=False,sharey=False)
			binsize_arr = np.arange(0.1,10,0.1)
			maxsnr = np.zeros(binsize_arr.size)
			for plotgroupid, dets_onegroup in enumerate([BGO,NaI]):
				timedata_onegroup = []
				GTI_onegroup = []
				for det in dets_onegroup:
					timedata_onedet = np.array([])					
					for hourstr in self.hourlist:
						year = hourstr[:4]
						yearshort = hourstr[2:4]
						month = hourstr[5:7]
						day = hourstr[8:10]
						hour = hourstr[11:13]+'z'
						thisdatadir = DATABASEDIR+'/'+year+'/'+month+'/'+day+'/'
						hourbegin_met = utc2met(hourstr)
						hourend_met=hourbegin_met+3600.00
						ttefile=glob(thisdatadir+'glg_tte_'+det+'_'+yearshort+month+day+'_'+hour+'_*')
						filenum=len(ttefile)
						if  filenum==1:
							hdu=fits.open(ttefile[0])
							t=hdu['EVENTS'].data.field(0)
							ch=hdu['EVENTS'].data.field(1)
							validindex=(t>=hourbegin_met) & (t<hourend_met) & (t>=self.Startmet) & (t<=self.Endmet)
							t=t[validindex]
							ch=ch[validindex]
							if len(t)>1:
								ch_index = (ch>=CH1) & (ch<=CH2)
								t=t[ch_index]
								if len(t)>1:
									timedata_onedet = np.concatenate([timedata_onedet, t])
					if len(timedata_onedet) > 1000: # considered enough data for being a valid timewindow
						GTI0_t1 = timedata_onedet[0]
						GTI0_t2 = timedata_onedet[-1]
						# A gap is considered existing where neighboring photons separate for larger than 5 second
						gapindex = (timedata_onedet[1:] - timedata_onedet[:-1]) > 5
						if np.sum(gapindex) >= 1:
							GTI_t1 = np.array(np.append([GTI0_t1],timedata_onedet[1:][gapindex]))
							GTI_t2 = np.array(np.append(timedata_onedet[:-1][gapindex],[GTI0_t2]))
							GTI_onedet = np.array([GTI_t1,GTI_t2])
						else:
							GTI_onedet = np.array([[GTI0_t1],[GTI0_t2]])
						timedata_onegroup.append(timedata_onedet)
						GTI_onegroup.append(GTI_onedet)
				nDet = len(timedata_onegroup) # number of valid dets in this group
				optimalGTI_onegroup = GTI_onegroup[0]
				for i in range(1,len(GTI_onegroup)):
					assert optimalGTI_onegroup.shape == GTI_onegroup[i].shape, "wrong GTI shape for:"+dets_onegroup[i]
					for GTIid in range(len(optimalGTI_onegroup[0])):
						optimalGTI_onegroup[0][GTIid] = max(optimalGTI_onegroup[0][GTIid],
																GTI_onegroup[i][0][GTIid])
						optimalGTI_onegroup[1][GTIid] = min(optimalGTI_onegroup[1][GTIid],
																GTI_onegroup[i][1][GTIid])
				nGTI = len(optimalGTI_onegroup[0])
				for binid, binwidth in enumerate(binsize_arr):
					net_onegroup = []
					for timedata in timedata_onegroup:
						net_onedet = []				
						for GTIid in range(nGTI):
							tbins = np.arange(optimalGTI_onegroup[0][GTIid], 
								optimalGTI_onegroup[1][GTIid]+binwidth, binwidth)
							histvalue, histbin=np.histogram(timedata,bins=tbins)
							rate = histvalue/binwidth
							r.assign('rrate',rate) 
							r("y=matrix(rrate,nrow=1)")
							fillPeak_hwi = str(max(int(5/binwidth),1))
							fillPeak_int = str(int(len(rate)/10))
							print(fillPeak_hwi,fillPeak_int)
							r("rbase=baseline(y,lam=6,hwi="+fillPeak_hwi
								+",it=10,int="+fillPeak_int+",method='fillPeaks')")
							r("bs=getBaseline(rbase)")
							r("cs=getCorrected(rbase)")
							bs = np.array(r('bs'))[0]
							cs = np.array(r('cs'))[0]
							# correct negative base to 0 and recover the net value to original rate
							corrections_index = (bs < 0)
							bs[corrections_index] = 0
							cs[corrections_index] = rate[corrections_index]
							net_onedet.append(cs)
						net_onegroup.append(net_onedet)
					combined_net_GTIs = [
							np.sum(np.array([net_onegroup[detid][GTIid] for detid in range(nDet)]),axis=0)
														 for GTIid in range(nGTI) ]
					combined_net = np.concatenate(combined_net_GTIs)
					mask = sigma_clip(combined_net,sigma=5,maxiters=5,stdfunc=mad_std).mask
					myfilter = list(map(operator.not_, mask))
					combined_net_median_part = combined_net[myfilter]
					loc,scale = stats.norm.fit(combined_net_median_part)
					snr = (combined_net - loc)/scale
					maxsnr[binid] = np.max(snr)
				axes[plotgroupid].tick_params(labelsize=25)
				axes[plotgroupid].plot(binsize_arr, maxsnr)
				#axes[plotgroupid].set_xlim([-5,10])
				axes[plotgroupid]
			axes[0].text(0.1,0.8,'BGOs',fontsize=25,
									transform=axes[0].transAxes)
			axes[1].text(0.1,0.8,'NaIs',fontsize=25,
									transform=axes[1].transAxes)
			#axes[0].legend(fontsize=15)
			fig.text(0.02, 0.5, 'Max SNR', ha='center',
						va='center',rotation='vertical',fontsize=25)
			fig.text(0.75, 0.05, 'Binsize (s)', ha='center',
								va='center',fontsize=25)
			plt.savefig(self.resultdir+'/max_snr_versus_binsize.png')
			plt.close()