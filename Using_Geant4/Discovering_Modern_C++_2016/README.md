Discovering Modern C++
--------------------------------------------

An Intensive Course for Scientists, Engineers, and Programmers

by P. Gottschling

Copyright @ 2016 Pearson Education, Inc.

https://github.com/petergottschling/discovering_modern_cpp


Compile and run an example.cpp source file
----------------------

1. Using G++ compiler
------------------

> g++ example.cpp -o example

> ./example

2. Using Make
--------------

> make example

(Typing example, and as .cpp is a standard file suffix for C++ sources, it will find example.cpp and call the system's default C++ compilers.)

> ./example

3. Using CMake
---------------

> gedit CMakeList.txt

and input:

cmake_minimum_required(VERSION 3.0)

add_executable(example example.cpp)

> cmake .

> make

> ./example
