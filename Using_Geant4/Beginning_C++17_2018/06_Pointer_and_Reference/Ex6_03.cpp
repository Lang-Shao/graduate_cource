// Revision of Example Ex6_03 by Shao
#include  <iostream>

int main()
{
	int count {};
	int* pcount {&count};

	*pcount = 12;
	std::cout << "The address of count (pcount) is " << pcount << std::endl;
	std::cout << "The count is " << *pcount << std::endl;

	const char* pstar1{ "Fatty Arbuckle" };

	std::cout << "The first letter of your lucky star is " << *pstar1 << std::endl;
	std::cout << "Your lucky star is " << pstar1 << std::endl;

}
