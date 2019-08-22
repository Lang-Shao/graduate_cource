Installation
------------

Download:
---------

http://geant4.web.cern.ch/support/download


Document:

http://geant4.web.cern.ch/support/user_documentation

http://geant4-userdoc.web.cern.ch/geant4-userdoc/UsersGuides/ForApplicationDeveloper/fo/BookForApplicationDevelopers.pdf

Document for installation:
--------------------------

https://www.hep.ucl.ac.uk/pbt/wiki/Software/Geant4/Installation

https://github.com/martraire/Install_Geant4

http://geant4-userdoc.web.cern.ch/geant4-userdoc/UsersGuides/InstallationGuide/fo/Geant4InstallationGuide.pdf


MY STEPS on ubuntu 18.04:
-----------

Pre-steps 
---------------------------

1. Update & Install g++ and cmake:

> sudo apt-get install build-essential

> sudo apt-get install cmake


2. Visualization using OpenGL and Qt:

a. Install X11

> sudo apt-get install libxaw7-dev libxaw7

To check if X11 is already installed and to know its version: 

> xdpyinfo|grep -i version

b. OpenGL (Mesa) 

> sudo apt-get install freeglut3 freeglut3-dev mesa-utils mesa-common-dev

> sudo apt-get install libglu1-mesa-dev libgl1-mesa-dev 

> sudo apt-get install libxerces-c-dev

Type this in a terminal to get much info about your OpenGL driver, including supported extensions:

> glxinfo | grep OpenGL

c. Qt

check qt version:

> qmake --version

Install:

> sudo apt install qt5-default

3. [Optional] Visualization using OpenInventor with Coin3D (a free implementation of Open Inventor)

a. download simage-1.7.1-src.zip at:

https://bitbucket.org/Coin3D/simage/downloads/

and install with:

> chmod +x configure

> ./configure

> make

> sudo make install

> make clean [optional]

b. download coin-4.0.0-src.zip at:

https://bitbucket.org/Coin3D/coin/downloads/

> sudo apt-get install cmake libblkid-dev e2fslibs-dev libboost-all-dev libaudit-dev

> chmod +x configure

> ./configure

> make 

> sudo make install

> make clean [optional]

c. download SoXt-1.3.0.tar.gz at (Newer versions should NOT be used):

https://bitbucket.org/Coin3D/coin/downloads/SoXt-1.3.0.tar.gz

The one from the following link does not work, which misses src/Inventor/Xt/common/sogui.cfg.in:

https://bitbucket.org/Coin3D/soxt/get/ef965f9f1b98.zip

This step has be wait after Coin has been installed.

> sudo apt-get install libfreetype6-dev libmotif-dev libxt-dev

> chmod +x configure

> ./configure

> make

> sudo make install

> make clean [optional]

d. download SoQt-1.5.0.tar.gz at:

https://bitbucket.org/Coin3D/coin/downloads/SoQt-1.5.0.tar.gz

However, this step could not succeed and might not be needed at all, since it appears to use QT4, but we have already install QT5 above.

4. Installation of additional librairies:

> sudo apt-get install libfontconfig1 libfontconfig1-dev libfreetype6-dev libx11-dev libxcursor-dev libxext-dev libxfixes-dev libxft-dev libxi-dev libxrandr-dev libxrender-dev

> sudo apt-get install xfonts-100dpi xfonts-75dpi gsfonts-x11

Formal steps
------------

1. Prepare directories

extract source to /home/lang/Software/geant4/geant4.10.05.p01

> mkdir /home/lang/Software/geant4/geant4.10.05.p01-install

> mkdir /home/lang/Software/geant4/geant4.10.05.p01-build

2. build

Build options may be set by passing their name and value to the cmake command via -D flags.

> cd /home/lang/Software/geant4/geant4.10.05.p01-build

- Put on the options for building the X11 OpenGL visualization driver with QT

- Also put on OpenInventor and RayTracer visualization drivers.

- Include Using GDML for geometry

> cmake -DCMAKE_INSTALL_PREFIX=/home/lang/Software/geant4/geant4.10.05.p01-install -DGEANT4_BUILD_MULTITHREADED=ON -DGEANT4_USE_OPENGL_X11=ON -DGEANT4_USE_QT=ON -DGEANT4_USE_INVENTOR=ON -DGEANT4_USE_RAYTRACER_X11=ON -DGEANT4_USE_GDML=ON -DGEANT4_INSTALL_DATA=ON -DEXPAT_LIBRARY=/usr/lib/x86_64-linux-gnu/libexpat.so ../geant4.10.05.p01

* If you are using anaconda for other purpose, use:

> conda deactivate

to get out the conda environment before cmake (which otherwise would use the compilers in conda instead of the system compilers as required by Geant4 build).

OUTPUT:

......

-- The following Geant4 features are enabled:

GEANT4_BUILD_CXXSTD: Compiling against C++ Standard '11'

GEANT4_BUILD_MULTITHREADED: Build multithread enabled libraries

GEANT4_BUILD_TLS_MODEL: Building with TLS model 'initial-exec'

GEANT4_USE_SYSTEM_EXPAT: Using system EXPAT library

GEANT4_USE_GDML: Building Geant4 with GDML support

GEANT4_USE_INVENTOR: Build OpenInventor Driver

GEANT4_USE_QT: Build Geant4 with Qt support

GEANT4_USE_RAYTRACER_X11: Build RayTracer driver with X11 support

GEANT4_USE_OPENGL_X11: Build Geant4 OpenGL driver with X11 support

-- Configuring done

-- Generating done

-- Build files have been written to: /home/lang/Software/geant4/geant4.10.05.p01-build

* The exact output will differ depending on the exact platform/compiler in use, but the last three lines should be the same to within path differences. These indicate a successful configuration.

3. make  

After the configuration has run, CMake will have generated Unix Makefiles for building Geant4. To run the build,
simply execute make in the build directory:

> make -jN  (DO NOT RUN THIS LINE DIRECTLY)

where N is the number of parallel jobs you require (e.g. if your CPU only has a dual core processor, you could set N to 2).

my case:

> make -j4

To know how many cores your CPU has: 

> cat /proc/cpuinfo | grep processor | wc -l

then the build will download the Geant4 datasets (~1.7 Gb) sepcifiled by -DGEANT4_INSTALL_DATA=ON.


4. make install

Once the build has completed, you can install Geant4 to the directory you specified earlier in
CMAKE_INSTALL_PREFIX by running in the build directory:

> make install

After installation
------------------

add to ~/.bashrc:

alias geant_init='. /home/lang/Software/geant4/geant4.10.05.p01-install/bin/geant4.sh'

Make an excutable program
-------------------------

1) initialize Geant4 

> geant_init


2) use cmake to build applications after initializing Geant4

for ./B1/CMakeList.txt

	./B1/exampleB1.cc

	./B1/include/... headers.hh ...

	./B1/src/... source.cc ...

> mkdir ./B1-build

> cd ./B1-build

> cmake ../B1

> make [-jN] [VERBOSE=1]

> ./exampleB1

Issues
-------

If the following warnings are shown when running geant4 script:

G4OpenGLXViewer::CreateFontLists XLoadQueryFont failed for font
  -adobe-courier-bold-r-normal--10-100-75-75-m-60-iso8859-1

G4OpenGLXViewer::CreateFontLists XLoadQueryFont failed for font
  -adobe-courier-bold-r-normal--11-80-100-100-m-60-iso8859-1

G4OpenGLXViewer::CreateFontLists XLoadQueryFont failed for font
  -adobe-courier-bold-r-normal--12-120-75-75-m-70-iso8859-1

....

My solution:

> sudo apt-get install xfonts-100dpi xfonts-75dpi gsfonts-x11

and 

> reboot

