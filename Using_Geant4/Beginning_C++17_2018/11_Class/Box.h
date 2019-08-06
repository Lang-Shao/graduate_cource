#ifndef BOX_H
#define BOX_H

class Box
{
private:
	double length {1.0};
	double width {1.0};
	double height {1.0};

public:
	Box(double lengthValue, double widthValue, double heightValue);
	explicit Box(double side);
	Box() = default;

	double volumn();

};

#endif
