https://github.com/FermiSummerSchool/fermi-summer-school


Full steps for installing fermitool and fermipy

==========

https://www.anaconda.com/distribution/
Download python 3 version with command line installer version
bash Anaconda3-2019.03-Linux-x86_64.sh
conda update conda
conda update anaconda

==========
https://github.com/fermi-lat/Fermitools-conda/wiki/Quickstart-Guide
Once you have downloaded and installed Anaconda, use the following command to download and setup your Fermitools environment:

conda create -n fermi -c conda-forge/label/cf201901 -c fermi fermitools

This command will create a conda environment named fermi and install the Fermitools and dependencies (including Fermitools-data) into the fermi environment.

The label cf201901 is currently required during installation to avoid mismatched symbol errors (see User Notes for details). We hope to make this unnecessary in a future release of the Fermitools.

============

To enable the Fermitools run:

conda activate fermi

This command activates the environment and runs the necessary activation scripts for the Fermitools. You will be dropped into the fermi conda environment with the Fermitools setup and ready to go!

============

If you already have an existing installation of the Fermitools on your machine, you can update by activating the conda environment (usually named fermi) the tools are installed in and running the conda update command.

conda activate fermi

conda update -c conda-forge/label/cf201901 -c fermi fermitools

============

If you already have an existing anaconda python installation then fermipy can be installed from the conda-forge channel as follows:

conda activate fermi

conda install -c conda-forge fermipy 
OR
conda install -c conda-forge/label/cf201901 fermipy 
==========
