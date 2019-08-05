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

http://geant4-userdoc.web.cern.ch/geant4-userdoc/UsersGuides/InstallationGuide/fo/Geant4InstallationGuide.pdf


MY STEPS on ubuntu 18.04:
-----------

Pre-steps for visualization using OpenGL:
---------------------------

All in all, install Mesa, Make and GCC/g++. Most Linux distributions rely on the Mesa3D project to provide their OpenGL implementation. This supplies libraries for regular OpenGL as well as OpenGL ES 1.x and 2.0.

> sudo apt-get install build-essential libgl1-mesa-dev

> sudo apt install mesa-utils

Type this in a terminal to get much info about your OpenGL driver, including supported extensions:

> glxinfo | grep OpenGL

Formal steps
------------

1) 

extract source to /home/lang/Software/geant4/geant4.10.05.p01

> mkdir /home/lang/Software/geant4/geant4.10.05.p01-install

> mkdir /home/lang/Software/geant4/geant4.10.05.p01-build

2)

Build options may be set by passing their name and value to the cmake command via -D flags.

> cd /home/lang/Software/geant4/geant4.10.05.p01-build

# put on the options for building the X11 OpenGL visualization driver

> cmake -DCMAKE_INSTALL_PREFIX=/home/lang/Software/geant4/geant4.10.05.p01-install -DGEANT4_BUILD_MULTITHREADED=ON -DGEANT4_USE_OPENGL_X11=ON -DGEANT4_INSTALL_DATA=ON -DEXPAT_LIBRARY=/usr/lib/x86_64-linux-gnu/libexpat.so ../geant4.10.05.p01

* If you are using anaconda for other purpose, use:

> conda deactivate

to get out the conda environment before cmake (which otherwise would use the compilers in conda instead of the system compilers as required by Geant4 build).

OUTPUT:

-- The C compiler identification is GNU 7.4.0
-- The CXX compiler identification is GNU 7.4.0
-- Check for working C compiler: /usr/bin/cc
-- Check for working C compiler: /usr/bin/cc -- works
-- Detecting C compiler ABI info
-- Detecting C compiler ABI info - done
-- Detecting C compile features
-- Detecting C compile features - done
-- Check for working CXX compiler: /usr/bin/c++
-- Check for working CXX compiler: /usr/bin/c++ -- works
-- Detecting CXX compiler ABI info
-- Detecting CXX compiler ABI info - done
-- Detecting CXX compile features
-- Detecting CXX compile features - done
-- Found EXPAT: /usr/lib/x86_64-linux-gnu/libexpat.so (found version "2.2.5") 
-- Looking for sys/types.h
-- Looking for sys/types.h - found
-- Looking for stdint.h
-- Looking for stdint.h - found
-- Looking for stddef.h
-- Looking for stddef.h - found
-- Check size of off64_t
-- Check size of off64_t - done
-- Looking for fseeko
-- Looking for fseeko - found
-- Looking for unistd.h
-- Looking for unistd.h - found
-- Configuring download of missing dataset G4NDL (4.5)
-- Configuring download of missing dataset G4EMLOW (7.7)
-- Configuring download of missing dataset PhotonEvaporation (5.3)
-- Configuring download of missing dataset RadioactiveDecay (5.3)
-- Configuring download of missing dataset G4PARTICLEXS (1.1)
-- Configuring download of missing dataset G4PII (1.3)
-- Configuring download of missing dataset RealSurface (2.1.1)
-- Configuring download of missing dataset G4SAIDDATA (2.0)
-- Configuring download of missing dataset G4ABLA (3.1)
-- Configuring download of missing dataset G4INCL (1.0)
-- Configuring download of missing dataset G4ENSDFSTATE (2.2)

-- The following Geant4 features are enabled:

GEANT4_BUILD_CXXSTD: Compiling against C++ Standard '11'

GEANT4_BUILD_MULTITHREADED: Build multithread enabled libraries

GEANT4_BUILD_TLS_MODEL: Building with TLS model 'initial-exec'

GEANT4_USE_SYSTEM_EXPAT: Using system EXPAT library

GEANT4_USE_OPENGL_X11: Build Geant4 OpenGL driver with X11 support


-- Configuring done

-- Generating done

-- Build files have been written to: /home/lang/Software/geant4/geant4.10.05.p01-build

* The exact output will differ depending on the exact platform/compiler in use, but the last three lines should be the same to within path differences. These indicate a successful configuration.

3) 

After the configuration has run, CMake will have generated Unix Makefiles for building Geant4. To run the build,
simply execute make in the build directory:

> make -jN  (DO NOT RUN THIS LINE DIRECTLY)

where N is the number of parallel jobs you require (e.g. if your machine has a dual core processor, you could set N to 2).

my case:

> make -j4

then the build will take a while to download the Geant4 datasets (~1.7 Gb) sepcifiled by -DGEANT4_INSTALL_DATA=ON.


4)

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

