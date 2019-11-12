THE GALACTIC AND EXTRA-GALACTIC ALL-SKY MWA SURVEY
------------------------------------------------

http://www.mwatelescope.org/gleam

https://github.com/ICRAR/gleamvo-client


Using Python3 in Python 2
---------------------

Most python3 code should work well in Python 2, too, if you add the following import statement in your Python 2 code:

> from __future__ import absolute_import, division, print_function


Suppress the warnings for rpy2
-----------------------------

The warning system in rpy2 uses Python's warnings module. As a consequence, you can switch off warnings using that package's filterwarnings() function. As already pointed out in a comment to another answer here this could be dangerous as not only R-related warnings are affected.

However, rpy2 comes with its own warning class, RRuntimeWarning. Therefore, you can switch off only this type of warning by

import warnings

from rpy2.rinterface import RRuntimeWarning

warnings.filterwarnings("ignore", category=RRuntimeWarning)


Beginning with 3.0 version, rpy2 does not use Python's warnings module anymore. It now relies on logging instead. The new solution would be:

from rpy2.rinterface_lib.callbacks import logger as rpy2_logger

import logging

rpy2_logger.setLevel(logging.ERROR)   # will display errors, but not warnings

My solution:

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

rbaseline issue:
----------------
rpy2.rinterface_lib.embedded.RRuntimeError: Error in if (length(x) == nrow * ncol) x <- matrix(x, nrow, ncol) else { :   missing value where TRUE/FALSE needed

warning: NAs produced by integer overflow.

Reason:  the data points are too many [> 46340] for rbaseline


h5py
-----

create_group method is not necesary, subgroups can be created on-the-fly
