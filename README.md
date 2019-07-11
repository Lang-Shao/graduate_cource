# graduate_cource

Tips for git & git hub

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
https://www.anaconda.com/distribution/


conda update conda

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

