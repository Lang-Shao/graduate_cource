Scope of variables shown in Figure 3-3 
---------------------------------------

You can define variables outside all of the functions in a program. Variables defined outside of all blocks
and classes are also called globals and have global scope (which is also called global namespace scope). This
means they’re accessible in all the functions in the source file following the point at which they're defined.
If you define them at the beginning of a source file, they'll be accessible throughout the file.

Global variables have static storage duration by default, so they exist from the start of the program until
execution of the program ends. Initialization of global variables takes place before the execution of main()
begins, so they’re always ready to be used within any code that’s within the variable’s scope. If you don’t
initialize a global variable, it will be zero-initialized by default. This is unlike automatic variables, which
contain garbage values when uninitialized.

The variable value1 at the beginning of the file is defined at global scope, as is value4, which appears
after the definition of main(). They will be initialized with zero by default. Remember, only global variables
have default initial values, not automatic variables. The lifetime of global variables is from the beginning of
program execution to when the program ends. Global variables have a scope that extends from the point
at which they’re defined to the end of the file. Even though value4 exists when execution starts, it can’t be
referred to in main() because main() isn’t within its scope. For main() to use value4, you would need to
move the definition of value4 to the beginning of the file.
The local variable called value1 in function() will hide the global variable of the same name. If you use
the name value1 in the function, you are accessing the local automatic variable of that name. To access the
global value1, you must qualify it with the scope resolution operator, ::. 

Here’s how you could output the values of the local and global variables that have the name value1:

std::cout << "Global value1 = " << ::value1 << std::endl;

std::cout << "Local value1 = " << value1 << std::endl;

Tips
-----

Common coding and design guidelines dictate that global variables are typically to be avoided, and
with good reason. Global constants are a noble exception to this rule. That is, global variables that are declared
with the const keyword. It is recommended to define all your constants only once, and global variables are
perfectly suited for that.


Usage
-----

1. Using G++ compiler
------------------

> g++ Ex3_03.cpp -o Ex3_03

> ./Ex3_03

2. Using Make
--------------

> make Ex3_03

(Typing just Ex3_03, and as .cpp is a standard file suffix for C++ sources, it will find Ex3_03.cpp and call the system's default C++ compilers.)

> ./Ex3_03

3. Using CMake
---------------

> cmake .

> make

> ./Ex3_03


