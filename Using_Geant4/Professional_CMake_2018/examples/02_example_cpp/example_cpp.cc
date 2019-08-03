// compile this C++ source code using cmake
// this example is listed in Figure 1-1 of a book (appended below) for a complete C++ program:
// https://github.com/Apress/beg-cplusplus17/blob/master/Beginning%20C%2B%2B%2017%20source%20code/Examples/Chapter%2001/Ex1_01.cpp

#include <iostream>

int main()
{
	int answer {42};

	std::cout << "The answer to life, the universe, and everything is "
			<< answer
			<< std::endl;
	
	return 0;
}

