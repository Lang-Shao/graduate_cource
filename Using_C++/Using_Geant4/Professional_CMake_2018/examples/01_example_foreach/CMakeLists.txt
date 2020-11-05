cmake_minimum_required(VERSION 3.0 FATAL_ERROR)

#project(trycmake)

set(A 1 2 3 4)
foreach(x ${A})
	message(${x})
endforeach()


foreach(xx IN LISTS A)
	message(${xx})
endforeach()

