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
sudo apt-get install python-dev git vim htop python-pip upstart lshw tcpdump redis-server
sudo pip install git-up redis
```

Reboot your pi after the above

## Wireless connection
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
