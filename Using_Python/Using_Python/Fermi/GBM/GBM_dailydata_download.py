# python script for downloading Fermi/GBM continuous daily data
# created by Shao on Aug. 12, 2018
import os
import ast
import sys
from ftplib import FTP_TLS as FTP
from glob import glob
from multiprocessing import Pool
nthread=60

#=============================================
downmethod=2
# three ways for specifying download task
# 1: set year list as in
#	downyearlist=['2013','2014']
# to run complete check by year
# downmethod=1
downyearlist=['2018']

# 2: set month list as in
#	downmonthlist=['201808']
# to run check by month
# downmethod=2
downmonthlist=['201906','201907','201908','201909']

# 3: provide daylist as in
#	downdaylist=['20130427','20150314']
# to run check by day
# downmethod=3
downdaylist=['20130427']

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
os.system('rm -rf '+filelistdir+'/*')

#============================================

fermidatabase='/fermi/data/gbm/daily/'
ftplink='https://heasarc.gsfc.nasa.gov/FTP/fermi/data/gbm/daily/'
f=FTP('129.164.179.23')

# wget downloading function for parallelization with multiprocessing
def wgetdown(link):
	os.system('wget --quiet --directory-prefix='+mydowndir+' '+link)

# function for moving downloaded files into corresponding directories
def movefile(filedir,targetdir):
	files=os.listdir(filedir)
	for filename in files:
		if filename[4:9]=='spech':
			year='20'+filename[16:18]
			month=filename[18:20]
			day=filename[20:22]
			#print(targetdir+year+'/'+month+'/'+day, filename)
			os.system('mv '+filedir+filename+' '+targetdir+year+'/'+month+'/'+day+'/')
		elif filename[4:9]=='poshi':
			year='20'+filename[16:18]
			month=filename[18:20]
			day=filename[20:22]
			#print(targetdir+year+'/'+month+'/'+day, filename)
			os.system('mv '+filedir+filename+' '+targetdir+year+'/'+month+'/'+day+'/')
		elif filename[4:9]=='ctime':
			year='20'+filename[13:15]
			month=filename[15:17]
			day=filename[17:19]
			#print(targetdir+year+'/'+month+'/'+day, filename)
			os.system('mv '+filedir+filename+' '+targetdir+year+'/'+month+'/'+day+'/')
		elif filename[4:9]=='cspec':
			year='20'+filename[13:15]
			month=filename[15:17]
			day=filename[17:19]
			#print(targetdir+year+'/'+month+'/'+day, filename)
			os.system('mv '+filedir+filename+' '+targetdir+year+'/'+month+'/'+day+'/')
		elif filename[4:7]=='tte':
			year='20'+filename[11:13]
			month=filename[13:15]
			day=filename[15:17]
			#print(targetdir+year+'/'+month+'/'+day, filename)
			os.system('mv '+filedir+filename+' '+targetdir+year+'/'+month+'/'+day+'/')

# method 1: function for checking files provided in a yearlist
def check_year(downyearlist):
	f.login()
	for year in downyearlist:
		myyearlist=os.listdir(mydatabase)
		if not year in myyearlist:
			os.mkdir(mydatabase+year)
		mymonthlist=os.listdir(mydatabase+year)
		f.cwd(fermidatabase+year)
		months=f.nlst()
		months.sort()
		for month in months:
			if not month in mymonthlist:
				os.mkdir(mydatabase+year+'/'+month)
			f.cwd(fermidatabase+year+'/'+month)
			os.mkdir(filelistdir+year+month)
			monthtestid=0
			days=f.nlst()
			days.sort()
			mydaylist=os.listdir(mydatabase+year+'/'+month)
			for day in days:
				f.login()
				print('Checking ==> '+year+'/'+month+'/'+day+':')
				if  not day in mydaylist:
					os.mkdir(mydatabase+year+'/'+month+'/'+day)
				listfile=open(filelistdir+year+month+'/'+year+month+day+'_newfile.txt', "w")
				testid=0
				deletefile=open(filelistdir+year+month+'/'+year+month+day+'_deletefile.txt', "w")
				deletetestid=0
				incompletefile=open(filelistdir+year+month+'/'+year+month+day+'_incompletefile.txt', "w")
				incompletetestid=0
				f.cwd(fermidatabase+year+'/'+month+'/'+day+'/current')
				files=f.nlst()
				files.sort()
				filenumber=len(files)
				myfilelist=os.listdir(mydatabase+year+'/'+month+'/'+day)
				myfilenumber=len(myfilelist)
				for filename in myfilelist:
					if not filename in files:
						print(filename, '***need to be removed which is currently not on server***')
						monthtestid=1
						deletetestid=1
						deletefile.write(mydatabase+year+'/'+month+'/'+day+'/'+filename+'\n')
				deletefile.close()
				if deletetestid == 0:
					os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_deletefile.txt')
				seq=0
				for filename in files:
					seq=seq+1
					print(filename, '(',seq,'/',filenumber,')')
					if filename not in myfilelist:
						monthtestid=1
						testid=1
						print(filename, '***is NEW, to be downloaded***')
						listfile.write(ftplink+year+'/'+month+'/'+day+'/current/'+filename+'\n')
					else:
						f.voidcmd('TYPE I')
						ftpfilesize=f.size(filename)
						myfilesize=os.path.getsize(mydatabase+year+'/'+month+'/'+day+'/'+filename)
						if not ftpfilesize==myfilesize:
							print(filename, '***has WRONG SIZE, to be downloaded***')
							monthtestid=1
							incompletetestid=1
							incompletefile.write(ftplink+year+'/'+month+'/'+day+'/current/'+filename+'\n')
				incompletefile.close()
				listfile.close()
				if testid == 0:
					os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_newfile.txt')
				if incompletetestid == 0:
					os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_incompletefile.txt')
				print('-- All',filenumber,'files examed --')
			if monthtestid == 0:
				os.system('rmdir '+filelistdir+year+month)
		#f.quit()


# method 2: function for checking files provided in a monthlist
def check_year_month(downmonthlist):
	for monthstring in downmonthlist:
		year=monthstring[:4]
		month=monthstring[4:6]
		myyearlist=os.listdir(mydatabase)
		if not year in myyearlist:
			os.mkdir(mydatabase+year)
		mymonthlist=os.listdir(mydatabase+year)
		if not month in mymonthlist:
			os.mkdir(mydatabase+year+'/'+month)
		f.login()
		f.prot_p()
		f.cwd(fermidatabase+year+'/'+month)
		os.mkdir(filelistdir+year+month)
		monthtestid=0
		days=f.nlst()
		days.sort()
		mydaylist=os.listdir(mydatabase+year+'/'+month)
		for day in days:
			f.login()
			print('Checking ==> '+year+'/'+month+'/'+day+':')
			if  not day in mydaylist:
				os.mkdir(mydatabase+year+'/'+month+'/'+day)
			listfile=open(filelistdir+year+month+'/'+year+month+day+'_newfile.txt', "w")
			testid=0
			deletefile=open(filelistdir+year+month+'/'+year+month+day+'_deletefile.txt', "w")
			deletetestid=0
			incompletefile=open(filelistdir+year+month+'/'+year+month+day+'_incompletefile.txt', "w")
			incompletetestid=0
			f.cwd(fermidatabase+year+'/'+month+'/'+day+'/current')
			files=f.nlst()
			files.sort()
			filenumber=len(files)
			myfilelist=os.listdir(mydatabase+year+'/'+month+'/'+day)
			myfilenumber=len(myfilelist)
			for filename in myfilelist:
				if not filename in files:
					print(filename, '***need to be removed which is currently not on server***')
					monthtestid=1
					deletetestid=1
					deletefile.write(mydatabase+year+'/'+month+'/'+day+'/'+filename+'\n')
			deletefile.close()
			if deletetestid == 0:
				os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_deletefile.txt')
			seq=0
			for filename in files:
				seq=seq+1
				print(filename, '(',seq,'/',filenumber,')')
				if filename not in myfilelist:
					monthtestid=1
					testid=1
					print(filename, '***is NEW, to be downloaded***')
					listfile.write(ftplink+year+'/'+month+'/'+day+'/current/'+filename+'\n')
				else:
					f.voidcmd('TYPE I')
					ftpfilesize=f.size(filename)
					myfilesize=os.path.getsize(mydatabase+year+'/'+month+'/'+day+'/'+filename)
					if not ftpfilesize==myfilesize:
						print(filename, '***has WRONG SIZE, to be downloaded***')
						monthtestid=1
						incompletetestid=1
						incompletefile.write(ftplink+year+'/'+month+'/'+day+'/current/'+filename+'\n')
			incompletefile.close()
			listfile.close()
			if testid == 0:
				os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_newfile.txt')
			if incompletetestid == 0:
				os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_incompletefile.txt')
			print('-- All',filenumber,'files examed --')
		#f.quit()
		if monthtestid == 0:
			os.system('rmdir '+filelistdir+year+month)



# method 3: function for checking files provided in a downdaylist
def check_year_month_day(downdaylist):
	for downdaystring in downdaylist:
		f.login()
		year=downdaystring[:4]
		month=downdaystring[4:6]
		day=downdaystring[6:8]
		if os.path.exists(mydatabase+year)== False:
			os.makedirs(mydatabase+year)
		if os.path.exists(mydatabase+year+'/'+month)== False:
			os.makedirs(mydatabase+year+'/'+month)
		myyearlist=os.listdir(mydatabase)
		mymonthlist=os.listdir(mydatabase+year)
		mydaylist=os.listdir(mydatabase+year+'/'+month)
		if not day in mydaylist:
			os.mkdir(mydatabase+year+'/'+month+'/'+day)
		os.mkdir(filelistdir+year+month)
		monthtestid=0
		print('Checking ==> '+year+'/'+month+'/'+day+':')
		listfile=open(filelistdir+year+month+'/'+year+month+day+'_newfile.txt', "w")
		testid=0
		deletefile=open(filelistdir+year+month+'/'+year+month+day+'_deletefile.txt', "w")
		deletetestid=0
		incompletefile=open(filelistdir+year+month+'/'+year+month+day+'_incompletefile.txt', "w")
		incompletetestid=0
		f.cwd(fermidatabase+year+'/'+month+'/'+day+'/current')
		files=f.nlst()
		files.sort()
		filenumber=len(files)
		myfilelist=os.listdir(mydatabase+year+'/'+month+'/'+day)
		myfilenumber=len(myfilelist)
		for filename in myfilelist:
			if not filename in files:
				print(filename, '***need to be removed which is currently not on server***')
				monthtestid=1
				deletetestid=1
				deletefile.write(mydatabase+year+'/'+month+'/'+day+'/'+filename+'\n')
		deletefile.close()
		if deletetestid == 0:
			os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_deletefile.txt')
		seq=0
		for filename in files:
			seq=seq+1
			print(filename, '(',seq,'/',filenumber,')')
			if filename not in myfilelist:
				monthtestid=1
				testid=1
				print(filename, '***is NEW, to be downloaded***')
				listfile.write(ftplink+year+'/'+month+'/'+day+'/current/'+filename+'\n')
			else:
				f.voidcmd('TYPE I')
				ftpfilesize=f.size(filename)
				myfilesize=os.path.getsize(mydatabase+year+'/'+month+'/'+day+'/'+filename)
				if not ftpfilesize==myfilesize:
					print(filename, '***has WRONG SIZE, to be downloaded***')
					monthtestid=1
					incompletetestid=1
					incompletefile.write(ftplink+year+'/'+month+'/'+day+'/current/'+filename+'\n')
		incompletefile.close()
		listfile.close()
		if testid == 0:
			os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_newfile.txt')
		if incompletetestid == 0:
			os.system('rm '+filelistdir+year+month+'/'+year+month+day+'_incompletefile.txt')
		print('-- All',filenumber,'files examed --')
		#f.quit()
	if monthtestid == 0:
		os.system('rmdir '+filelistdir+year+month)






# check files provided in a downdaylist
if downmethod==1:
	check_year(downyearlist)

if downmethod==2:
	check_year_month(downmonthlist)

if downmethod==3:
	check_year_month_day(downdaylist)

# download newfile and incompletefile, remove deletefile
yearmonthlist=os.listdir(filelistdir)
for yearmonth in yearmonthlist:
	daysfile_new=glob(filelistdir+yearmonth+'/*_newfile.txt')
	daysfile_incom=glob(filelistdir+yearmonth+'/*_incompletefile.txt')
	daysfile_new.sort()
	daysfile_incom.sort()
	n_new=len(daysfile_new)
	n_incom=len(daysfile_incom)
	if (n_new >= 1):
		for cfile in daysfile_new:
			with open(cfile,'r') as fid:
				lines=fid.readlines()
			print('*** Downloading newfile:',lines)
			if __name__ == '__main__':
				p = Pool(nthread)
				p.map(wgetdown, lines)
			print('************* Finish downloading above newfiles. ********** ')
			movefile(mydowndir,mydatabase)

	if (n_incom >= 1):
		for cfile in daysfile_incom:
			with open(cfile,'r') as fid:
				lines=fid.readlines()
			print('*** Downloading incomfile:',lines)
			if __name__ == '__main__':
				p = Pool(nthread)
				p.map(wgetdown, lines)
			print('************* Finish downloading above incomfiles. ********** ')
			movefile(mydowndir,mydatabase)

	deletefile=glob(filelistdir+yearmonth+'/*_deletefile.txt')
	deletefile.sort()
	n_del=len(deletefile)
	if (n_del>=1):
		for cfile in deletefile:
			with open(cfile,'r') as fid:
				delfilelinks=fid.readlines()
			for flink in delfilelinks:
				print, 'deleting '+flink
				os.system('rm '+flink)
