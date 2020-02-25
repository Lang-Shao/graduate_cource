* 2.2.4 Packages

In Python, a package is nothing more than a directory that contains modules (.py files) and a special file that tells Python to treat the directory as a package (`__init__.py`). 

This file is often empty, but it can be used for more complex management of imports. 

You can nest packages in a process similar to creating an initial package. Create a directory with an `__init__.py` file, and put modules or packages inside:


>math

>	`__init__.py`
>	statistics
>		`__init__.py`
>		std.py
>		cdf.py
>	calculus
>		`__init__.py`
>		integral.py
>	...

Importing the integral module works like before, with additional prefixes to get to the module of interest:

> from math.calculus import integral

> import math.calculus.integral

Note that from math import calculus.integral won't work.


