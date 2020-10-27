from glob import glob
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from astropy.io import fits

bn = '150314205'
det = 'n9'
binwidth = 0.064
viewt1 = -10
viewt2 = 20


databasedir = '/db/Data/Fermi_GBM_burst/data/'
year = '20'+bn[0:2]
datadir = databasedir+'/'+year+'/bn'+bn
ttefile = glob(datadir+'/'+'glg_tte_'+det+'_bn'+bn+'_v*.fit')
assert len(ttefile) == 1
hdu = fits.open(ttefile[0])
trigtime = hdu['Primary'].header['TRIGTIME']
data = hdu['EVENTS'].data
time = data.field(0)-trigtime
ch = data.field(1)

time1 =  time[(ch >= 20) & (ch <= 40)]
time2 =  time[(ch >= 40) & (ch <= 80)]
tbins = np.arange(viewt1,viewt2+binwidth,binwidth)
counts1, _ = np.histogram(time1,bins=tbins)
counts2, _ = np.histogram(time2,bins=tbins)
counts_forplot1 = np.concatenate(([counts1[0]],counts1))
counts_forplot2 = np.concatenate(([counts2[0]],counts2))

fig, axes = plt.subplots(2,1,figsize=(10, 12),sharex=True,sharey=False)
axes[0].plot(tbins,counts_forplot1,drawstyle='steps')
axes[1].plot(tbins,counts_forplot2,drawstyle='steps')
plt.savefig('./lc.png')
plt.close()




