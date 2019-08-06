#include "Box.h"
#include  <iostream>

Box::Box(double lv, double wv, double hv): 	length {lv}, width {wv}, height {hv}
{
	std::cout << "Contructor 1 for regular box called."  << std::endl;

}

Box::Box(double side): 	Box{side, side, side}
{
	std::cout << "Contructor 2 for cube called."  << std::endl;

}


double Box::volumn()
{
	return length*width*height;
}

int main()
{
	Box myBox1{10.0, 10.0, 10.0};
	std::cout << "Volumn of the myBox1 is " << myBox1.volumn() << std::endl;

	Box secondBox{4.0};
	std::cout << "Volumn of secondBox is " << secondBox.volumn() << std::endl;
}
