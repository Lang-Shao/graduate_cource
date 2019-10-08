from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
import logging
rpy2_logger.setLevel(logging.ERROR) 

'''Beginning with 3.0 version, rpy2 does not use Python's warnings module anymore. 
It now relies on logging instead. The new solution would be:

from rpy2.rinterface_lib.callbacks import logger as rpy2_logger
import logging
rpy2_logger.setLevel(logging.ERROR)   # will display errors, but not warnings

If you want to filter specific warnings only, use:

rpy2_logger.addFilter(lambda record: 'notch went outside hinges' not in record.msg)
See LogRecord class specification for available fields for advanced filtering.
'''

#import warnings
#from rpy2.rinterface import RRuntimeWarning
#warnings.filterwarnings("ignore", category=RRuntimeWarning)

import rpy2.robjects as robjects
from rpy2.robjects import r
import rpy2.robjects.numpy2ri
robjects.numpy2ri.activate()
robjects.r("library(baseline)")
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

t = np.linspace(0,100,101)
rate = 10*stats.norm(50,1).pdf(t) + np.random.rand(101)
print(t)
plt.plot(t,rate)
plt.show()

r.assign('rrate',rate)
r("y=matrix(rrate,nrow=1)")
binwidth = 1
fillPeak_hwi = str(int(5/binwidth))
fillPeak_int = str(int(len(rate)/10))
r("rbase=baseline(y,lam=6,hwi="+fillPeak_hwi+",it=10,int="+fillPeak_int+",method='fillPeaks')")
r("bs=getBaseline(rbase)")
r("cs=getCorrected(rbase)")
bs = np.array(r('bs'))[0]
cs = np.array(r('cs'))[0]

# correct negative base to 0 and recover the net value to original rate
corrections_index = (bs < 0)
bs[corrections_index] = 0
cs[corrections_index] = rate[corrections_index]

plt.plot(t,rate)
plt.plot(t,bs)
plt.show()