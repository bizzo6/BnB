# BnB

## Overview
A low cost smart and secure home automation server running on your Raspberry Pi

# Setting Up

## Dependencies

Following are needed:

```
sudo apt-get install redis-server
sudo pip install flask flask-restful flask-httpauth redis
sudo pip install pyfcm
```

## SSL Context

To creating a key-pair for the web server:

```
cd ~/pi/Bnb/
mkdir certs
cd certs
openssl genrsa 1024 > host.key
chmod 400 host.key
openssl req -new -x509 -nodes -sha1 -days 1000 -key host.key > host.cert
```

## Installing upstart script
Copy the upstart configuration files from /init to your RPi under /etc/init/

Now you can start the bnb service using the upstart commands (it will also start once the RPi is booted):
```
sudo start bnb
sudo stop bnb
sudo status bnb
```

## Network devices

Some basic Wifi Dongles that support this setup:

* Ralink RT5370
** Chipset: 
** Driver: rt2800usb
** Monitor mode: Supported

* Realtek RTL8188CUS
** Chipset: Realtek RTL8188CUS
** Driver: rtl819x
** Monitor mode: NOT Supported

* Edimax EW-7811Un
** Chipset: Realtek RTL8188CUS
** Driver: rtl819x
** Monitor mode: NOT Supported

Check your setup using:
```
sudo lshw -class network
```

## Find my Pi
Use nmap to find the ip address your Pi got from the local DHCP:
```
sudo nmap -sP 192.168.1.0/24 | awk '/^Nmap/{ip=$NF}/B8:27:EB/{print ip}'
```
Note: replace 192.168.1.0 with your ip segment