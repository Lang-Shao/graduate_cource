import os

def get_usersjar():
	usersjar = "/home/lang/Software/HEASARC-Xamin/users.jar"
	return usersjar

def query_fermigbrst(cdir='./'):
	fermigsol = cdir+'/fermigsol.txt'
	if not os.path.exists(fermigsol):
		usersjar = get_usersjar()
		assert os.path.exists(usersjar), """'users.jar' is not available! 
			download users.jar at:
			https://heasarc.gsfc.nasa.gov/xamin/distrib/users.jar
			and update the path of usersjar in 'personal_settings.py'."""
		java_ready = os.system("java --version")
		assert not java_ready, """java not properly installed!
			Install Oracle Java 10 (JDK 10) in Ubuntu or Linux Mint from PPA
			$ sudo add-apt-repository ppa:linuxuprising/java
			$ sudo apt update
			$ sudo apt install oracle-java10-installer"""
		fields = ("name,duration,peak_rate,total_counts,"
			"gbm_sunward_detectors,gbm_trigger,rhessi_flare_num")
		print('querying fermigsol catalog using HEASARC-Xamin-users.jar ...')
		query_ready = os.system("java -jar "+usersjar+" table=fermigsol fields="
				+fields+" sortvar=name output="+cdir+"/fermigsol.txt")
		assert not query_ready, 'failed in querying fermigsol catalog!'
		print('successful in querying fermigsol catalog!')
	return fermigsol
	
query_fermigbrst()