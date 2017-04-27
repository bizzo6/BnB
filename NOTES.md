# Notes:


## MotionEye

We will use the MotionEye as our DVR for this example.

### Installation:
TBD: installing MotionEye goes here..

### Adding SSL with nginx:
see: https://blog.radityakertiyasa.com/2015/03/raspberrypi-nginx-secure-reverse-proxy-server/
And now add SSL with letsencrypt using this tutorial:
see:  https://blog.dantup.com/2016/03/installing-lighttpd-php7-and-letsencrypt-on-raspberry-pi-raspbian-jessie-lite/

```
sudo apt-get install nginx
letsencrypt certonly --webroot -w /usr/share/nginx/html -d your.domain.com
```

Convert the generated pem to crt/key:
```
openssl x509 -outform der -in certificate.pem -out certificate.crt
```

```
sudo /etc/init.d/nginx start | stop
sudo vim /etc/nginx/sites-available/sitenamehere
```

#### Renewal
Every 90 days just run (make sure you open port 80 on your router):
```
sudo letsencrypt renew
sudo /etc/init.d/nginx stop
sudo /etc/init.d/nginx start
```
and now disable back your port forwarding for port 80 for better security

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

## Some Raspbian tweaks:

Rotate logs and cleanup:
```
sudo logrotate -f /etc/logrotate.conf
sudo rm /var/log/*.1
sudo rm /var/log/*.gz
```

See which folder taking so much space:
```
du -Pshx /path/here/* 2>/dev/null
```

Start/Stop services:
```
sudo systemctl stop nginx.service
sudo systemctl start nginx.service

sudo systemctl stop motioneye.service
sudo systemctl start motioneye.service
```


## OrangePi Zero Stuff

Flask and GPIO example:
https://www.hackster.io/chedadsp/hello-orange-pi-zero-cfaa26

Install:
sudo apt-get install python-dev python-setuptools python-pip
sudo pip install flask


