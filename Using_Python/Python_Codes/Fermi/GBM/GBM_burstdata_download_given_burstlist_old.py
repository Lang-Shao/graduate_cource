# python script for downloading Fermi/GBM triggered burst data
# created by Shao on Oct. 8, 2018
import os
import ast
import sys
from ftplib import FTP_TLS as FTP
from glob import glob
from multiprocessing import Pool
nthread=60

#downburstlist=['bn091010113','bn101208498','bn120129580','bn120323507','bn120624309','bn130310840','bn140508128','bn180113011','bn180703949','bn181119606']
downburstlist=['bn190114873']


fermidatabase='/fermi/data/gbm/bursts/'
ftplink='https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/'
f=FTP('129.164.179.23')

topdir='./'
mydatabase=topdir+'data/' 
filelistdir=topdir+'filelist/'
mydowndir=topdir+'downloaded/'
if os.path.exists(filelistdir)== False:
	os.makedirs(filelistdir)
if os.path.exists(mydowndir)== False:
	os.makedirs(mydowndir)
if os.path.exists(mydatabase)== False:
	os.makedirs(mydatabase)



def wgetdown(link):
	os.system('wget --quiet --directory-prefix='+mydowndir+' '+link)


for downburst in downburstlist:
	os.system('rm -rf '+filelistdir+'/*')
	os.system('rm -rf '+mydowndir+'/*')
	year='20'+downburst[2:4]
	if os.path.exists(mydatabase+year)== False:
		os.makedirs(mydatabase+year)
	f.login()
	f.prot_p()
	f.cwd(fermidatabase+year+'/'+downburst+'/current/')
	files=f.nlst()
	with open(filelistdir+'list.txt','w') as newlistfile:
		for filename in files:
			newlistfile.write(ftplink+year+'/'+downburst+'/current/'+filename+'\n')
	with open(filelistdir+'list.txt') as downlistfile:
		filelinks=downlistfile.readlines()
		
	if __name__ == '__main__':
		print('Downloading burst:',downburst, '...')
		p = Pool(nthread)
		p.map(wgetdown, filelinks)
	os.system('mkdir '+mydatabase+year+'/'+downburst)
	os.system('mv '+mydowndir+'/* '+mydatabase+year+'/'+downburst)
