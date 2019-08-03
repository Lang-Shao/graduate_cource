// compile this C++ source code using cmake
// this example is listed in Figure 1-1 for a complete C++ program

#include <iostream>

int main()
{
	int answer {42};

	std::cout << "The answer to life, the universe, and everything is "
			<< answer
			<< std::endl;
	
	return 0;
}

