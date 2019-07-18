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

issue note on July 17, 2019:

如果出现编码问题：类似错误如下UnicodeDecodeError: 'ascii' codec can't decode byte 0xe5 in position 4: ordinal not in range(128)，这是由于python2中的编码bug，需要在python目录/lib/python2.7/site-packages/中新建一个文件：
sitecustomize.py,其中包含下列代码。
import sys
sys.setdefaultencoding('utf-8')

随后再修改系统默认编码:
export LANG=en_US:UTF-8
export LANGUAGE=en_US:en

=========

issue note on July 18, 2019:

KeyError: 'PROJ_LIB' when: from mpl_toolkits.basemap import Basemap

export PROJ_LIB=$CONDA_PREFIX/share/proj  # Linux and OS X
