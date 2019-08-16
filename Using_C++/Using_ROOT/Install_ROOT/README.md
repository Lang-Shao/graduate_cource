Installation
------------

Download:
---------

https://github.com/root-project/root

(https://root.cern.ch/

https://root.cern.ch/downloading-root)

Document:
---------

https://root.cern.ch/root/htmldoc/guides/users-guide/ROOTUsersGuide.html


Document for installation:
--------------------------

https://root.cern.ch/root/htmldoc/guides/users-guide/ROOTUsersGuide.html#appendix-a-install-and-build-root

https://github.com/root-project/root

MY STEPS on ubuntu 18.04:
-----------

1. Download source

> mkdir ~/Software/ROOT

> cd ~/Software/ROOT/

> git clone https://github.com/root-project/root.git

2. cmake and make

> mkdir build

> cd build

> cmake ../root

> make -j4

where 4 is the number of parallel jobs you require (e.g. if your CPU only has a dual core processor, you could set 4 to 2).

To know how many cores your CPU has:

> cat /proc/cpuinfo | grep processor | wc -l

3. Setup environment and run ROOT

for once put the following line in ~/.bashrc as in:

> alias root_init='source ~/Software/ROOT/build/bin/thisroot.sh'

use the following command in a new terminal to setup ROOT environment:

> root_init

To run ROOT GUI:

> root

(or simply for once put the following line in ~/.bashrc as in:

> alias root_init='source ~/Software/ROOT/build/bin/thisroot.sh ; root'

)


