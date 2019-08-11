Usage
-----

For each example XX, the only source file is XX/CMakeLists.txt

To test cmake using:

> cd XX

> cmake .


Chapter 2. Setting Up A Project
-------------------------------

A fundamental part of CMake is the concept of a project having both a source directory and a
binary directory. The source directory is where the CMakeLists.txt file is located and the project’s
source files and all other files needed for the build are organized under that location. The source
directory is frequently under version control with a tool like git, subversion, or similar.

The binary directory is where everything produced by the build is created. It is often also called the
build directory. For reasons that will become clear in later chapters, CMake generally uses the term
binary directory, but among developers, the term build directory tends to be in more common use.
This book tends to prefer the latter term since it is generally more intuitive. CMake, the chosen
build tool (e.g. make, Visual Studio, etc.), CTest and CPack will all create various files within the build
directory and subdirectories below it. Executables, libraries, test output and packages are all
created within the build directory. CMake also creates a special file called CMakeCache.txt in the
build directory to store various information for reuse on subsequent runs.
