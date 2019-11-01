# modify this file for personal settings
# the changes of which should be ignored during each commit

import socket

def get_usersjar():
	usersjar = "/home/lang/Software/HEASARC-Xamin/users.jar"
	return usersjar

def get_burstdatabasedir():
	if socket.gethostname() == 'SHebtu':
		databasedir = '/diskb/Database/Fermi/gbm_burst/data/'
	else:
		databasedir = '/home/lang/work/GBM/burstdownload/data/'
	return databasedir

def get_dailydatabasedir():
	if socket.gethostname() == 'SHebtu':
		dailydatabasedir= '/diska/Fermi_GBM_daily/data/'
	else:
		dailydatabasedir = '/home/lang/work/GBM/daily/data/'
	return dailydatabasedir
