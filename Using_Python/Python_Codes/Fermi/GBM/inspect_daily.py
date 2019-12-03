from GBM_daily_lib import *
import matplotlib
matplotlib.use('Agg')

@timer
def inspect_timewindow(winname, StartUTC, EndUTC, binwidth=0.64, resultdir='./'):
	slice1 = TIMEWINDOW(winname, StartUTC, EndUTC, binwidth=binwidth, resultdir=resultdir)
	slice1.make_ttedata()
	slice1.plot_raw_lc_make_GTI_and_base()
	slice1.plot_base()
	#t0 = 486983822.3906 # TGF 2016-06-07 09:16:58.390600
	#slice1.plot_netlc_giventimerange(t0-10,t0+10)
	#slice1.plot_netlc_snr_giventimerange(t0-10,t0+10)
	slice1.plot_netlc()
	slice1.check_netlc_gaussian_distribution()
	slice1.plot_netlc_snr()
	slice1.plot_combined_snr(binwidth=binwidth)
	slice1.plot_raw_countmap()

############
# RUN MAIN #
############
if __name__ == '__main__':
	#main()
	cdir = os.getcwd()
	resultdir = cdir+'/results/'
	#inspect_timewindow('window1', '2019-01-14 00:00:00',
	#		 '2019-01-14 23:59:59.9999', resultdir=resultdir)
	inspect_timewindow('window2', '2019-01-14 18:54:00',
			 '2019-01-14 21:05:00', resultdir=resultdir)
	#inspect_timewindow('tgf', '2016-06-07 09:16:08.3906',
	#		 '2016-06-07 09:17:48.3906', binwidth=0.001, resultdir=resultdir)
	#inspect_timewindow('solarflare', '2019-05-06 04:30:00',
	#		 '2019-05-06 05:59:00', binwidth=0.64, resultdir=resultdir)
