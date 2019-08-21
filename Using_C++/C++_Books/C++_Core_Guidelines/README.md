Online reference for C++
-----------------------------

C++ Core Guidelines

Editors:

- Bjarne Stroustrup

- Herb Sutter

https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md

http://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines

Notes
-------------------------

A programmer should be familiar with:

- The guidelines support library

https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md#S-gsl

- The ISO C++ Standard Library

https://github.com/isocpp/CppCoreGuidelines/blob/master/CppCoreGuidelines.md#S-stdlib

- Whatever foundation libraries are used for the current project(s)

`vector` and `array` containers
----------------

- To initialize a vector with a number of elements, use ()-initialization. To initialize a vector with a list of elements, use {}-initialization.

	vector<int> v1(20);  // v1 has 20 elements with the value 0 (vector<int>{})

	vector<int> v2 {20}; // v2 has 1 element with the value 20

Prefer the {}-initializer syntax.

- If `vector` suits your needs but you don't need the container to be variable size, use `array` instead.
