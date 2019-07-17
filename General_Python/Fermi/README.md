https://github.com/FermiSummerSchool/fermi-summer-school


Full steps for installing fermitool and fermipy
https://www.anaconda.com/distribution/
Download python 3 version with command line installer version
bash Anaconda3-2019.03-Linux-x86_64.sh
conda update conda
conda update anaconda
==========
conda install -c conda-forge fermipy 
OR
conda install -c conda-forge/label/cf201901 fermipy 
==========
conda create -n fermi -c conda-forge/label/cf201901 -c fermi fermitools
