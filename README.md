# BnB

## Overview
A low cost smart and secure home utility running on your Raspberry Pi

# Setting Up

## Dependencies

Following are needed:

```
sudo pip install flask flask-restful flask-httpauth
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
