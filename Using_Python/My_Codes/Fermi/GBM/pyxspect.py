from GBM_catalog_spectralanalysis_lib import *
import matplotlib
matplotlib.use('Agg')


def inspect_GRB(bnname,resultdir):
	grb = GRB(bnname,resultdir)
	if grb.dataready:
		#currently useful
		grb.rawlc(viewt1=-50,viewt2=300,binwidth=0.064)
		grb.base(baset1=-50,baset2=300,binwidth=0.064) #MUST RUN
		grb.plot_gaussian_significance_net_rate()
		grb.check_pulse()
		grb.countmap()
		#remove basedir to save disk space
		#grb.removebase()

		#currently not useful
		#grb.check_gaussian_net_rate()
		#grb.plot_gaussian_level_over_net_lc()
		#grb.check_snr()
		#grb.skymap(catalog_ra, catalog_dec)
		#grb.plotbase()
		#grb.check_gaussian_total_rate()
		#grb.check_poisson_rate()
		#grb.plot_time_resolved_net_spectrum()
		#grb.check_poisson_time_resolved_net_spectrum()
		#grb.netlc()
		#grb.rsp()
		#grb.multi_binwidth_base()
		#grb.check_mb_base_snr(viewt1=-1,viewt2=25)
		#grb.check_mb_base_gaussian_net_rate()
		'''
		timebins = [0,5]
		nslice = len(timebins)-1
		for i in np.arange(nslice):
			grb.phaI(slicet1=timebins[i],slicet2=timebins[i+1]) 
			grb.specanalyze('slice'+str(i))
		'''

	else:
		print(bnname, ": missing data!")

############
# RUN MAIN #
############
if __name__ == '__main__':
	#main()
	cdir = os.getcwd()
	resultdir = cdir+'/results/'
	inspect_GRB('bn190829830',resultdir)
