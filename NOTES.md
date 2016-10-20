# Notes:


## kerberos


Some missing packages:
sudo apt-get install libtiff-tools

https://www.scalescale.com/tips/nginx/install-memcached-ubuntu/
sudo apt-get install memcached
sudo apt-get install php5-memcached

And than do this for the above to take effect:
sudo service php5-fpm restart.


See nginx errors here:
/var/log/nginx/nginx_error.log



## Monitor Mode:

To set a wlan device into monitor mode:
```
sudo ifconfig wlan0 down
sudo iwconfig wlan0 mode monitor
sudo ifconfig wlan0 up
sudo iwconfig wlan0 channel 1
```

Using pcapy to sniff around:
```
sudo apt-get install python-pcapy
```



https://bitbucket.org/LaNMaSteR53/wuds/src/a8f5c04aecf3d46e23a16fe74695738e94611b0f/core.py?fileviewer=file-view-default


http://hackoftheday.securitytube.net/2013/03/wi-fi-sniffer-in-10-lines-of-python.html
http://askldjd.com/2014/01/15/a-reasonably-fast-python-ip-sniffer/

https://bitbucket.org/LaNMaSteR53/wuds