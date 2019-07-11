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

conda update conda

conda update conda-build # in case conda-build raises warnings

conda activate enviname # activate into an environment

conda activate  # back to base environment


conda install packname # run in given environment

conda install --channel channelname <package>
conda install -c channelname <package> # the same


