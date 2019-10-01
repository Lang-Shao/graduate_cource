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

