from GBM_daily_lib import *
import matplotlib
matplotlib.use('Agg')

@timer
def inspect_timewindow(winname, StartUTC, EndUTC, resultdir='./'):
	slice1= TIMEWINDOW(winname, StartUTC, EndUTC, resultdir=resultdir)
	slice1.plot_rawlc_genGTI()
	slice1.binned_netlc()
	slice1.plot_netlc()
	slice1.check_netlc_gaussian_distribution()
	slice1.plot_netlc_significance()

############
# RUN MAIN #
############
if __name__ == '__main__':
	#main()
	cdir = os.getcwd()
	resultdir = cdir+'/results/'
	#inspect_timewindow('window1', '2019-01-14 20:54:00',
	#		 '2019-01-14 21:05:00', resultdir=resultdir)
	inspect_timewindow('window2', '2019-01-14 18:54:00',
			 '2019-01-14 21:05:00', resultdir=resultdir)
