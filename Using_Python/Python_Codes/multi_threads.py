import numpy as np
import datetime
from threading import Thread
from multiprocessing import Pool
from decorators import timer

@timer
def checksequential():
	for _ in range(1,40):
		a = 0
		while a < 10000000:
			a += 1
		print(datetime.datetime.now().time())
		
def checkparallel_part():
	a = 0
	while a < 10000000:
		a += 1
	print(str(datetime.datetime.now().time()))

@timer
def checkparallel():
	threads = []
	for x in range(1,40):
		t = Thread(target=checkparallel_part)
		t.start()
		threads.append(t)

	for t in threads:
		t.join()

ncore=40
def singlethread(i):
	a = 0
	while a < 10000000:
		a += 1
	print(datetime.datetime.now().time())
		
@timer
def checkmultiprocessing():
	if __name__ == '__main__':
		p = Pool(ncore)
		p.map(singlethread,np.arange(40))
		
checksequential()

print("\n *** Now check parallel threads *** \n")
checkparallel()

print("\n *** Now check multiprocessing *** \n")
checkmultiprocessing()

