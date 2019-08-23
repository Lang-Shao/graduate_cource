Tips for conda
-----------------

- Download python 3 version with command line installer version

https://www.anaconda.com/distribution/

> bash Anaconda3-2019.03-Linux-x86_64.sh

- update 

> conda update conda

> conda update anaconda

> conda update conda-build # in case conda-build raises warnings

- If you do not want conda to auto activate its base environment:

> conda config --set auto_activate_base False

To review your selection:

> conda config --show | grep auto_activate_base

- list environment

> conda-env list

- list the packages in current environment:

> conda list

- create environment

> conda create --name myenv

> conda create -n myenv # the same

- activate an environment

> conda activate myenv # activate into an environment

> conda activate  # back to conda base environment

> conda deactivate # log out of conda to use system python environment

- install a package in current environment

> conda install packname # run in given environment

> conda uninstall packname # run in given environment to remove the unwanted packages that cause incompatible issues

- install a package from a given channel

> conda install --channel channelname <package>

> conda install -c channelname <package> # the same

> conda install -c anaconda jupyter

> conda install -c conda-forge spherical-geometry

> conda install -c anaconda basemap 

> conda install -c conda-forge pymc3

> conda install -c r rpy2 

- update a package from a given channel

> conda update -c conda-forge pymc3

try jupyter online
---------------------
https://jupyter.org/try
