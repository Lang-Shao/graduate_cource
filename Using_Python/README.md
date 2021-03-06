Tips for conda
-----------------

- Download python 3 version with command line installer version

https://www.anaconda.com/distribution/

> bash Anaconda3-2019.03-Linux-x86_64.sh

- recommend miniconda over anaconda 

https://docs.conda.io/en/latest/miniconda.html

- update 

> conda update conda # updating conda itself

(> conda update -n base -c defaults conda)

(> conda update anaconda)

> conda update conda-build # in case conda-build raises warnings

- If you do not want conda to auto activate its base environment:

> conda config --set auto_activate_base False

To review your selection:

> conda config --show | grep auto_activate_base

- list environment

> conda info --envs

> conda-env list # the same

- list the packages in current environment:

> conda list

- create environment

> conda create --name myenv

> conda create -n myenv # the same

- activate an environment

> conda activate myenv # activate into an environment

> conda activate  # back to conda base environment

> conda deactivate # log out of conda to use system python environment

- exporting an environment file

> conda env export > $file_name

- creating an environment from a file

> conda env create -f $file_name

- install a package in current environment

> conda install packname # run in given environment

> conda uninstall packname # run in given environment to remove the unwanted packages that cause incompatible issues

- install a package from a given channel

> conda install --channel channelname <package>

> conda install -c channelname <package> # the same

- adding conda-forge to your channels

> conda config --add channels conda-forge

- To list all of the versions of spherical-geometry available on your platform with

> conda search spherical-geometry [--channel conda-forge]

- exmaple:

> conda install python=3.6

> conda install jupyter

> conda install -c conda-forge spherical-geometry (conflicts with python3.7, works with 3.5 or 3.6)

or 

> conda install -c conda-forge/label/cf201901 spherical-geometry (works with 3.6)

> conda install -c conda-forge basemap 

> conda install -c conda-forge pymc3

> conda install -c r r 

> conda install -c r rpy2

- update a package from a given channel

> conda update -c conda-forge pymc3py


try jupyter online
---------------------

https://jupyter.org/try

Setup Jupyter notebook default folder in Anaconda
---------------------------------------------------

http://darques.eu/blog/index.php/2017/08/25/setup-jupyter-notebook-default-folder-in-anaconda/


Tips for jupyter
-----------------

https://ndres.me/post/best-jupyter-notebook-extensions/

%lsmagic: Run this in a cell to list all available IPython magics

autoreload: Autoreloads external files without having to restart the notebook. You may want to reload submodules if you've edited the code in one.
To enable it:

%load_ext autoreload

%autoreload 2
