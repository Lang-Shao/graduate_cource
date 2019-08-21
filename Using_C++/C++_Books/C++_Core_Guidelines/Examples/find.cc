#include<iostream>
#include<vector>
#include<array>
#include<algorithm>

using namespace std;

int main()
{

//  concatenate a vector<char>
	vector<char> helloVector {'h','e','l','l','o','!'};
/*	string helloString;
	for (auto letter:helloVector)
	{
		helloString += letter;
	}
	
*/ // Complicate 
	string helloString {begin(helloVector),end(helloVector)}; //better


	cout << helloString << endl;

	// find a num in a vector<int>
	vector<int> s {10,20,30};
	int num;
	cout << "Input a number:" << endl;
	cin >> num;
	s.push_back(40);
	//list<int>::iterator it = find(lst.begin(), lst.end(), 10); // older coding style
	auto it = find(begin(s), end(s), num); // better!
	if (it != s.end())
    {
        cout << "Found it!" << endl;
    }
    else
	{
		cout << "Did not find it." << endl;
    }

	// find a string in a vector<string>
	vector<string> v {"hello","world","!!"};
	string val;
	cout << "Input a string:" << endl;
	cin >> val;
	v.push_back("good");
	auto p = find(begin(v),end(v),val);
	if (p != v.end())
    {
        cout << "Found it!" << endl;
    }
    else
	{
		cout << "Did not find it." << endl;
    }

	//If vector suits your needs but you don't need the container to be variable size, use array instead.
	//array<string,size>

	array<string,3> v1 {"hello","world","!!"};
	string val1;
	cout << "Input another string:" << endl;
	cin >> val1;
	auto p1 = find(begin(v1),end(v1),val1);
	if (p1 != v1.end())
    {
        cout << "Found it!" << endl;
    }
    else
	{
		cout << "Did not find it." << endl;
    }

}
