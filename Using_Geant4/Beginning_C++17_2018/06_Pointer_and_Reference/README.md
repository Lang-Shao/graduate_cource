Difference between pointers to numeric type and char type 
------------------------------------------------------

A pointer to a numeric type must be dereferenced (using *) to output the value to which it points, whereas applying the insertion operator to a pointer to type char that is not dereferenced presumes that the pointer contains the address
of a null-terminated string. If you output a dereferenced pointer to type char, the single character at that
address will be written to cout. 

Usage
-----

> cmake .

> make

> ./Ex6_03
