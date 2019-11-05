from GBM_catalog_spectralanalysis_lib import *
import matplotlib
matplotlib.use('Agg')

@timer
def inspect_GRB(pars):
	bnname, resultdir = pars
	grb = GRB(bnname,resultdir)
	if grb.dataready:
		#currently useful
		grb.rawlc(viewt1=-50,viewt2=300,binwidth=0.064)
		grb.base(baset1=-50,baset2=300,binwidth=0.64) #MUST RUN
		grb.plot_gaussian_significance_net_rate()
		grb.check_pulse()
		grb.plot_significance_lightcurve()
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
	bn = ['bn190114873','bn180720598','bn190829830']
	ncore = set_ncore()
	p = Pool(ncore)
	total_num = len(bn)
	p.map(inspect_GRB, zip(bn,[resultdir]*total_num))
	#for bn in ['bn180720598','bn190829830']:
	#	print('Processing: ',bn)
	#	inspect_GRB(bn,resultdir)
