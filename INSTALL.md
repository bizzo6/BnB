# INSTALLATION

## Getting your RPi Ready

Create a boot SD Card with the latest Raspbian OS image (Lite)
https://www.raspberrypi.org/downloads/raspbian/

```
sudo dd bs=4M if=2016-03-18-raspbian-jessie.img of=/dev/mmcblk0
```
After dd is done (it will take a while), run 'sync' and remove the SDCard. Now Plug it again so new partition will appear.
Use gparted (under Ubuntu) to extend the newly created partition to the full size of your SDCard:
```
gksudo gparted
```
Remove the SD and place in the RPi to boot up.

Now find your RPi on the network:
```
sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
```
Note: replace 192.168.1.0 with your ip address range

Login using default credentials:
```
User: pi
Password: raspberry
```

Use the raspi-config tool to setup basic configs:
```
sudo raspi-config
```

Make sure to select:
* Expend filesystem
* Change password for default user
* Enable SSH (from advanced)
* Enable Pi Camera
* Select to boot to shell without auto-login
* Select locality and timezone

Reboot to test configuration and re-login.
Check your IP address (when RPi is connected with LAN cable to your router):
```
ifconfig eth0
```

Use this IP to connect using SSH next time.

## Getting things ready

To make sure you are running the latest software, drivers and firmwares, do the followings:
```
sudo apt-get update
sudo apt-get upgrade
```

Now install some basic system packages:
```
sudo apt-get install python-dev git vim htop python-pip lshw tcpdump redis-server

```

Set the local timezone by:
```
sudo cp /usr/share/zoneinfo/Israel /etc/localtime
```
or just search the zoneinfo folder for your relevant location

Reboot your pi after the above

## Setting up motion-eye

see: https://github.com/ccrisan/motioneye

Installation guide for Raspbian: https://github.com/ccrisan/motioneye/wiki/Install-On-Raspbian
After you finish up, visit your main MotionEye webapp under:
```
http://127.0.0.1:8765
```
User is "admin" and password is empty for now.
Setup the passwords for the "admin" as well as the "user".
User good password also for the "user" - we will be using this credential for viewing secured streams. 

### Adding a basic RTSP camera:

Start adding you cameras using the Web interface of MotionEye at **http://127.0.0.1:8765/** Default login is "admin" and
 a blank password.
 
A supported IP camera should have an RTSP stream available. For example:
* Foscam C1 - rtsp://[IP Address]:554/videoMain
* Foscam C2 - rtsp://[IP Address]:88/videoMain

Note: you'll better set a static IP or a reserved DHCP for your IP cameras
 
On MotionEye web interface, add a new camera and select "Network Camera" as type, enter the full RTSP
url as above examples, and don't forget the user:password pair for authentication. MotionEye will automatically 
detect the correct video stream type (you can select between TCP to UDP and stuff like that).

Lastly, make sure the streaming option is enabled and add the "Basic" authentication method. We will use this
one masked under HTTPS so it will be secure to watch your streams from other apps like TinyCamPro for Android (
which is our weapon of choice).

## Setup Webserver and SSL
Install the following:
```
sudo apt-get install nginx
sudo apt-get install lighttpd
sudo apt-get install letsencrypt
```

lighttpd will be used for presenting a default page when accessing port 80 of the RPi but
mainly used for the letsencrypt client to authenticate your domain and IP.

nginx will be the main server service used to proxy all other services as well
as introduce SSL using your new generated certificate.


### Basic Web Server
The basic webserver is the lighttpd and the root folder is located under:
```
/var/www/html

```
We are alreayd proxified by nginx so the default index page is the **index.nginx-debian.html**
 and you can replace it's content with whatever default page you want.
 
### Nginx Configuration
 Not it's time to make sure Nginx is configured as needed - optimized for the RPi as
 well as using the most recent security protocols.
 See this tutorial for the full story:
 
 ```
 https://blog.radityakertiyasa.com/2015/03/raspberrypi-nginx-secure-reverse-proxy-server/
 ```
 Bsically what you need to do is:
 
 #### Configure a site
 
 You can duplicate the default configuration under **/etc/nginx/sites-available** and create a new symlink:
 ```
cd /etc/nginx/sites-available \
sudo cp default mysite \
cd /etc/nginx/sites-enabled \
sudo rm default \
sudo ln -s /etc/nginx/sites-available/mysite
```
later on we will update this site configuration to reflect the usage of SSL as well as setting up SSL proxy
to specific services like streaming video, web apps etc.

An example can be found under the project folder "system" - **mysite.conf**

#### Set security configuration for nginx

Lots of relevant security features are not set as default, and this tutorial helps setting it all up and also understand
what exactly we are doing:

https://blog.radityakertiyasa.com/2015/03/raspberrypi-nginx-secure-reverse-proxy-server/

basically, you will need to add a **security.conf** extension for the nginx configuration, and also generate a
 unique pem file for extended security. So to make things quicker, copy the security.conf file from the porject "conf" folder
 to the following on your system:
 
 ```
 /etc/nginx/conf.d/security.conf
 ```
 
 and also generate the relevant pem file under that same folder. This action might take a while:
 
 ```
 cd /etc/nginx/conf.d
 sudo openssl dhparam -out dh4096.pem 4096
 ```
  
 
### Requesting a certificate
For the first time, you will need to setup port forwarding so accessing your external IP address in port 80 will
give you the default index page on lighttpd. You will also need to update DNS records so your domain is
aligned with your external IP.
Once you setup all the above, you can let the letsecnrypt do the rest of the heavy lifting. This includes
generating pages on your index webservice and authenticating that indeed you are in control of this server and domain (but actually requesting the generated pages from the letsecrypt servers)

NOTE: make sure port 80 is open and forwarded to the RPi IP so letsencrypt servers can access the page they
generated inside lighttpd server.
```
sudo letsencrypt certonly --webroot -w /var/www/html -d www.yourdomain.com
```

The new cert chain is saved now at: **/etc/letsencrypt/live/www.yourdomain.com/fullchain.pem**
Now let's create links for nginx can work with those:
```commandline
sudo mkdir /etc/nginx/ssl
sudo ln -s /etc/letsencrypt/live/www.bananablat.com/cert.pem /etc/nginx/ssl/cert.pem
sudo ln -s /etc/letsencrypt/live/www.bananablat.com/fullchain.pem /etc/nginx/ssl/fullchain.pem
sudo ln -s /etc/letsencrypt/live/www.bananablat.com/privkey.pem /etc/nginx/ssl/privkey.pem
```

Note than on the site configuration on nginx we already refers to this folder **/etc/nginx/ssl**

Now let's restart nginx:
```commandline
sudo /etc/init.d/nginx configtest
sudo /etc/init.d/nginx stop
sudo /etc/init.d/nginx start
```
NOTE: if you get errors, you might want to stop lighttpd as it is using the same port 80:
```commandline
sudo /etc/init.d/lighttpd stop
sudo systemctl disable lighttpd
```

## Setting up BnB

### Prerequisites

Install some python packages:
```commandline
sudo pip install slackclient redis flask flask-restful flask-httpauth
```











## (Optional) Wireless connection
Connect your wifi dongle to the RPi and power it up.

To scan for available networks:
```
sudo iwlist wlan0 scan
```

Now edit your wpa-supplicant config file to include your wifi network:
```
sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
```

Add these lines to the end of the file:
```
network={
    ssid="ESSID"
    psk="PASSWORD"
}
```

For changes to take place, restart the interface:
```
sudo ifdown wlan0
sudo ifup wlan0
```

Wait a sec, and check if you get an IP:
```
ifconfig wlan0
```
