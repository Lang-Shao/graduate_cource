Tips for my graduate cource
-----------------------------


Tips for git & git hub
-----------------------


$ git config --global user.name "John Doe" 

$ git config --global user.email johndoe@example.com

$ git config --global core.excludesfile "~/.gitignore"

$ gedit ~/.gitignore and add:

*.pyc

*.txt

*.eps

*.fit

*.fits

*.png

*.jpg

\_\_pycache\_\_/

.ipynb_checkpoints/

.Rhistory

results/

bad_sample/

[on windows: git config --global core.excludesfile "%USERPROFILE%\.gitignore"

and the file should be at C:\User\Administrator\.gitignore]

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

Git on windows
-----------------

https://git-scm.com/download/win


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
