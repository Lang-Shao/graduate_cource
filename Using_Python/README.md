Tips for conda
-----------------

https://www.anaconda.com/distribution/

- update 

> conda update conda

> conda update anaconda

> conda update conda-build # in case conda-build raises warnings

- list environment

> conda-env list

- list the packages in current environment:

> conda list

- create environment

> conda create --name myenv

> conda create -n myenv # the same

- activate an environment

conda activate myenv # activate into an environment

conda activate  # back to conda base environment

conda deactivate # log out of conda to use system python environment

- install a package in current environment

conda install packname # run in given environment

conda uninstall packname # run in given environment to remove the unwanted packages that cause incompatible issues

conda install --channel channelname <package>

conda install -c channelname <package> # the same

conda install -c anaconda jupyter

conda install -c conda-forge spherical-geometry

conda install -c anaconda basemap 

conda install -c r rpy2 

try jupyter online
---------------------
https://jupyter.org/try
