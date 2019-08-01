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

1) 

extract source to /home/lang/Software/geant4/geant4.10.05.p01

> mkdir /home/lang/Software/geant4/geant4.10.05.p01-install

> mkdir /home/lang/Software/geant4/geant4.10.05.p01-build

2)

Build options may be set by passing their name and value to the cmake command via -D flags.

> cd /home/lang/Software/geant4/geant4.10.05.p01-build

> cmake -DCMAKE_INSTALL_PREFIX=/home/lang/Software/geant4/geant4.10.05.p01-install -DGEANT4_INSTALL_DATA=ON -DEXPAT_LIBRARY=/usr/lib/x86_64-linux-gnu/libexpat.so ../geant4.10.05.p01

* If you are using anaconda for other purpose, use:

> conda deactivate

to get out the conda environment before cmake (which otherwise would use the compilers in conda instead of the ystem compilers as required by Geant4 build).

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
GEANT4_USE_SYSTEM_EXPAT: Using system EXPAT library

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

then the build will take a while to download the Geant4 datasets sepcifiled by -DGEANT4_INSTALL_DATA=ON.


4)

Once the build has completed, you can install Geant4 to the directory you specified earlier in
CMAKE_INSTALL_PREFIX by running in the build directory:

> make install
