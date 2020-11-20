Main Page:

http://gecam.ihep.ac.cn/

Test Data:

http://gecam.ihep.ac.cn/testdata.jhtml

Response Generator:

http://gecam.ihep.ac.cn/xgwd.jhtml


##install Heasoft

https://heasarc.gsfc.nasa.gov/lheasoft/download.html

Complete HEASoft source code (all mission & general-use software) (2.7 Gb / 4.6 Gb unpacked)

https://heasarc.gsfc.nasa.gov/lheasoft/ubuntu.html

Before configure/make, do change:

> export PYTHON=/usr/bin/python

into:

> export PYTHON=/your_anaconda_dir/bin/python/

Then there is no need to hamke for pyxspec.



## for spherical-geometry, better use python=3.6 for gecam


##install gecam caldb

Put the following into your ".bahsrc":

> export HEADAS=/home/lang/Software/heasoft-6.28/x86_64-pc-linux-gnu-libc2.31

> export CALDB=/home/lang/Software/heasoft-6.28/caldb

> alias heainit=". $HEADAS/headas-init.sh"

> alias caldbinit=". $CALDB/software/tools/caldbinit.sh"

Put the followiing into your "caldbinit.sh":



>  CALDB=/home/lang/Software/heasoft-6.28/caldb; export CALDB

>  caldb_software_path=$CALDB/software/

>  export PYTHONPATH=$PYTHONPATH:$caldb_software_path

>  echo CALDB_PATH $CALDB

>  echo PYTHONPATH $PYTHONPATH


> if [ -z "$CALDBCONFIG" ]; then

>    CALDBCONFIG=$CALDB/software/tools/caldb.config; export CALDBCONFIG

> fi 

> if [ -z "$CALDBALIAS" ]; then

>    CALDBALIAS=$CALDB/software/tools/alias_config.fits; export CALDBALIAS

> fi 


