# python script for downloading Fermi/GBM team-verified burst data
# created by Shao on Jul. 16, 2018
import os
import ast
import sys
from ftplib import FTP_TLS as FTP
from glob import glob
from multiprocessing import Pool
nthread=50


downmethod=2
#=============================================
# if downmethod=1
downyearlist=['2019']

# if downmthod=2
downmonthlist=['2019009','201910','201911','201912']

#============================================
# check the following directories
topdir='./'
filelistdir=topdir+'filelist/'
mydowndir=topdir+'downloaded/'
mydatabase=topdir+'data/'  # most important one: the database
if os.path.exists(filelistdir)== False:
	os.makedirs(filelistdir)
if os.path.exists(mydowndir)== False:
	os.makedirs(mydowndir)
if os.path.exists(mydatabase)== False:
	os.makedirs(mydatabase)

os.system('rm -rf '+mydowndir+'/*.*')
os.system('rm -rf '+filelistdir+'/*.*')

#============================================

fermidatabase='/fermi/data/gbm/bursts/'
ftplink='https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/bursts/'
f=FTP('129.164.179.23')

# wget downloading function for parallelization with multiprocessing
def wgetdown(link):
	os.system('wget --quiet --directory-prefix='+mydowndir+' '+link)

# function for moving downloaded files into corresponding directories
def movefile():
	cfiles=os.listdir(mydowndir)
	for filename in cfiles:
		bnindex=filename.find('bn')
		year='20'+filename[bnindex+2:bnindex+4]
		burstname=filename[bnindex:bnindex+11]
		os.system('mv -f '+mydowndir+filename+' '+mydatabase+year+'/'+burstname+'/')

# function for checking files provided in a downyearlist
def check_year(downyearlist):
	f.login()
	f.prot_p()
	for year in downyearlist:
		myyearlist=os.listdir(mydatabase)
		if not year in myyearlist:
			os.mkdir(mydatabase+year)
		myburstlist=os.listdir(mydatabase+year)
		f.cwd(fermidatabase+year)
		bursts=f.nlst()
		bursts.sort()
		newfile=open(filelistdir+year+'_newfile.txt', "a+")
		newtestid=0
		deletefile=open(filelistdir+year+'_deletefile.txt', "a+")
		deletetestid=0
		for burst in bursts:
			if not burst in myburstlist:
				os.mkdir(mydatabase+year+'/'+burst)
			f.cwd(fermidatabase+year+'/'+burst+'/current')
			files=f.nlst()
			files.sort()
			filenumber=len(files)
			myfilelist=os.listdir(mydatabase+year+'/'+burst)
			myfilenumber=len(myfilelist)
			print('Checking ==> '+year+'/'+burst+':')
			for filename in myfilelist:
				if not filename in files:
					print(filename, '***need to be removed which is currently not on server***')
					deletetestid=1
					deletefile.write(mydatabase+year+'/'+burst+'/'+filename+'\n')
			seq=0
			for filename in files:
				seq=seq+1
				print(filename, '(',seq,'/',filenumber,')')
				if filename not in myfilelist:
					print(filename, '***is NEW, to be downloaded***')
					newtestid=1
					newfile.write(ftplink+year+'/'+burst+'/current/'+filename+'\n')
				else:
					f.voidcmd('TYPE I')
					ftpfilesize=f.size(filename)
					myfilesize=os.path.getsize(mydatabase+year+'/'+burst+'/'+filename)
					if not ftpfilesize==myfilesize:
						print(filename, '***has WRONG SIZE, to be downloaded***')
						newtestid=1
						newfile.write(ftplink+year+'/'+burst+'/current/'+filename+'\n')
			print('-- All',filenumber,'files examed --')
		newfile.close()
		deletefile.close()
		if newtestid == 0:
			os.system('rm -f '+filelistdir+year+'_newfile.txt')
		if deletetestid == 0:
			os.system('rm -f '+filelistdir+year+'_deletefile.txt')
	f.quit()

# function for checking files provided in a downmonthlist
def check_month(downmonthlist):
	f.login()
	f.prot_p()
	for month in downmonthlist:
		year=month[:4]
		myyearlist=os.listdir(mydatabase)
		if not year in myyearlist:
			os.mkdir(mydatabase+year)
		myburstlist=os.listdir(mydatabase+year)
		f.cwd(fermidatabase+year)
		bursts=f.nlst()
		bursts.sort()
		newfile=open(filelistdir+month+'_newfile.txt', "a+")
		newtestid=0
		deletefile=open(filelistdir+month+'_deletefile.txt', "a+")
		deletetestid=0
		for burst in bursts:
			if burst[2:6]==month[2:]:
				if not burst in myburstlist:
					os.mkdir(mydatabase+year+'/'+burst)
				f.cwd(fermidatabase+year+'/'+burst+'/current')
				files=f.nlst()
				files.sort()
				filenumber=len(files)
				myfilelist=os.listdir(mydatabase+year+'/'+burst)
				myfilenumber=len(myfilelist)
				print('Checking ==> '+year+'/'+burst+':')
				for filename in myfilelist:
					if not filename in files:
						print(filename, '***need to be removed which is currently not on server***')
						deletetestid=1
						deletefile.write(mydatabase+year+'/'+burst+'/'+filename+'\n')
				seq=0
				for filename in files:
					seq=seq+1
					print(filename, '(',seq,'/',filenumber,')')
					if filename not in myfilelist:
						print(filename, '***is NEW, to be downloaded***')
						newtestid=1
						newfile.write(ftplink+year+'/'+burst+'/current/'+filename+'\n')
					else:
						f.voidcmd('TYPE I')
						ftpfilesize=f.size(filename)
						myfilesize=os.path.getsize(mydatabase+year+'/'+burst+'/'+filename)
						if not ftpfilesize==myfilesize:
							print(filename, '***has WRONG SIZE, to be downloaded***')
							newtestid=1
							newfile.write(ftplink+year+'/'+burst+'/current/'+filename+'\n')
				print('-- All',filenumber,'files examed --')
		newfile.close()
		deletefile.close()
		if newtestid == 0:
			os.system('rm -f '+filelistdir+month+'_newfile.txt')
		if deletetestid == 0:
			os.system('rm -f '+filelistdir+month+'_deletefile.txt')
	f.quit()

# check files provided in a downdaylist
if downmethod==1:
	check_year(downyearlist)
	# download newfile and incompletefile, remove deletefile
	for year in downyearlist:
		file_new=glob(filelistdir+year+'_newfile.txt')
		n_new=len(file_new)
		if (n_new == 1):
			cfile=file_new[0]
			with open(cfile,'r') as fid:
				lines=fid.readlines()
			print('*** Downloading newfile:',lines)
			if __name__ == '__main__':
				p = Pool(nthread)
				p.map(wgetdown, lines)
			print('************* Finish downloading above newfiles. ********** ')
			movefile()

		deletefile=glob(filelistdir+year+'_deletefile.txt')
		n_del=len(deletefile)
		if (n_del == 1):
			cfile=deletefile[0]
			burstname=cfile[:11]
			with open(cfile,'r') as fid:
				delfilelinks=fid.readlines()
			for flink in delfilelinks:
				print, 'deleting '+flink
				os.system('rm -f '+flink)
elif downmethod==2:
	check_month(downmonthlist)
	# download newfile and incompletefile, remove deletefile
	for month in downmonthlist:
		file_new=glob(filelistdir+month+'_newfile.txt')
		n_new=len(file_new)
		if (n_new == 1):
			cfile=file_new[0]
			with open(cfile,'r') as fid:
				lines=fid.readlines()
			print('*** Downloading newfile:',lines)
			if __name__ == '__main__':
				p = Pool(nthread)
				p.map(wgetdown, lines)
			print('************* Finish downloading above newfiles. ********** ')
			movefile()

		deletefile=glob(filelistdir+month+'_deletefile.txt')
		n_del=len(deletefile)
		if (n_del == 1):
			cfile=deletefile[0]
			burstname=cfile[:11]
			with open(cfile,'r') as fid:
				delfilelinks=fid.readlines()
			for flink in delfilelinks:
				print, 'deleting '+flink
				os.system('rm -f '+flink)
	


