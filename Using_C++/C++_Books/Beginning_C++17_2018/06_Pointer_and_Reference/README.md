Difference between pointers to numeric type and char type 
------------------------------------------------------

A pointer to a numeric type must be dereferenced (using *) to output the value to which it points, whereas applying the insertion operator to a pointer to type char that is not dereferenced presumes that the pointer contains the address
of a null-terminated string ('\0'). If you output a dereferenced pointer to type char, the single character at that
address will be written to cout. 

Usage
-----

1. Using G++ compiler
------------------

> g++ Ex6_03.cpp -o Ex6_03

> ./Ex6_03

2. Using Make
--------------

> make Ex6_03

(Typing just Ex6_03, and as .cpp is a standard file suffix for C++ sources, it will find Ex6_03.cpp and call the system's default C++ compilers.)

> ./Ex6_03

3. Using CMake
---------------

> cmake .

> make

> ./Ex6_03
