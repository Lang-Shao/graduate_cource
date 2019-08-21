Tips for my graduate cource
-----------------------------


Tips for git & git hub
-----------------------


$ git config --global user.name "John Doe"   

$ git config --global user.email johndoe@example.com

$ git config --global core.excludesfile "~/.gitignore"

$ gedit ~/.gitignore and add:

*.pyc

\_\_pycache\_\_/

.ipynb_checkpoints/


$ git config --global credential.helper cache

$ git config --global credential.helper 'cache --timeout=720000'


$ git rm -cached filename


$ git clone github_link.git

$ git log

$ git status

$ git add .

$ git commit -am "message"

$ git push

$ git pull


Tips for conda
-----------------

https://www.anaconda.com/distribution/

conda update conda

conda update anaconda

conda update conda-build # in case conda-build raises warnings


conda create --name myenv

conda create -n myenv # the same

conda list

conda activate myenv # activate into an environment

conda activate  # back to conda base environment

conda deactivate # log out of conda to use system python environment

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

Issues
--------

Internet connection is too slow for 'git clone':

https://blog.csdn.net/github_34965845/article/details/80610060

> sudo gedit /etc/hosts

add:

192.30.253.112	github.com

151.101.185.194	github.global.ssl.fastly.net

151.101.184.249	global-ssl.fastly.net

(To find the latest ip's of above web addresses at:

https://www.ipaddress.com/

or

> nslookup global-ssl.fastly.net

)

then restart networking

> sudo /etc/init.d/networking restart


Linux Bash
----------

http://tldp.org/HOWTO/Bash-Prog-Intro-HOWTO.html#toc6

https://ryanstutorials.net/bash-scripting-tutorial/bash-if-statements.php
