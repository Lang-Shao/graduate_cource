issues:
-------

* OSError: [Errno 24] Too many open files

> ulimit -a (check open files)

> sudo vim /etc/security/limits.conf

add:

\* soft nofile 10240

\* hard nofile 10240

then

> reboot

> ulimit -a

* ImportError: libiconv.so.2: cannot open shared object file: No such file or directory

> conda activate gbm

> conda install -c r libiconv


* use unoffically updated baseline-1.2.3 from Kristian Hovde Liland

> install.packages('limSolve')

> install.packages('/home/lang/Downloads/baseline_1.2-3.tar.gz',repos=NULL,type='source')
