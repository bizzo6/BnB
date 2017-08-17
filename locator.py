# -*- coding: UTF-8 -*-
'''
Created: 10/04/2016

@author: bizzo6

Module: Locator (BnB)
Description:
    The locator module is meant to find the presence of specific persons in the area of the system in order to trigger
    other modules actions. e.g. Start the motion detection security camera alerts once you elave the appartment.
    The locator uses passive sniffing of Wifi communication and looks for probe requests created by cellphones.
    Probes (especially active scanning probes) will be sent out from the device while it is active and will include the
    MAC address which is used to identify the device.
    Notes:
        - Device that have wifi ON will send out probs - even if activly associated to a network
        - Devices with Wifi turned OFF will not scan for networks thus will not send out the probe above.
        - To enable locator functionality even if wifi module is OFF, we ride on the Google Location Services function
          that scans for networks around for better location estimation EVEN IF WIFI IS OFF. Good for google, good for
          us.. well at least in this case.

'''
import logging
from json import dumps

from conf.configuration import *
import pcapy
import struct
import subprocess
import libs
from datetime import datetime

# datalink types: http://www.tcpdump.org/linktypes.html
LINKTYPE_IEEE802_11_RADIOTAP = 0x7F
LINKTYPE_IEEE802_11 = 0x70

class locator(object):

    def __init__(self, interface=LOCATOR_MONITOR_INTERFACE, defaultchannel=LOCATOR_DEFAULT_CHANNEL_INT):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        self.ipc = libs.bnbipc.bnbipc()

        self.interface = interface
        self.channel = defaultchannel

        self.initinterface()
        self.sniffer = self.initsniffer(self.interface)

    def initinterface(self):
        '''
        Inits the interface to monitor mode and default channel
        :param interface:
        :return:
        '''
        self.logger.info("Setting interface %s to monitor mode", self.interface)
        self.runcmd(["ifconfig", self.interface, "down"])
        self.runcmd(["iwconfig", self.interface, "mode", "monitor"])
        self.runcmd(["ifconfig", self.interface, "up"])
        self.runcmd(["iwconfig", self.interface, "channel", str(self.channel)])
        self.logger.info("Interface %s is in monitor mode on channel %d", self.interface, self.channel)
        return True

    def runcmd(self, cmd):
        self.logger.debug("Running: %s", cmd)
        try:
            subprocess.check_output(cmd)
            return True
        except Exception as ex:
            self.logger.error("Exception in runcmd: %s", str(ex))
            return False

    def initsniffer(self, interface):
        self.logger.info("Initializing pcapy sniffer on %s interface", interface)
        try:
            return pcapy.open_live(interface, LOCATOR_PCAPY_SNAPLEN_INT, 1, 0)
        except Exception as ex:
            self.logger.error("Exception in Initiating pcapy: %s", str(ex))

    def probehandler(self, mac, ssid, rssi):
        self.logger.info("Probe: %s --> %s (%ddB)", mac, ssid, rssi)
        # push to the locator redis queue:
        probe = {
            'ts': str(datetime.now()),
            'mac': mac,
            'ssid': ssid,
            'rssi': rssi
            }
        self.ipc.pushlocatorprobe(dumps(probe))
        # Check if there is an open location entity:
            # get last entity
            # if last update was older than 5min (location_timeout):
                # start a new one
                # set RSSI
                # Set start time to current time
                # Add the probe SSID to the macs list (for reference)
            # if last update was less than 5min (location_timeout):
                # update current entity with new close time
                # Set RSSI for new value only in greater than what is already there (just for debug for now)
                # Add the probe SSID to the macs list (for reference)

    def packethandler(self, pkt):
        '''
        The packet includes a radio-tap header, followed by the standard IEEE802.11 frames.
        We will splitt the radiotap header, and use it to get RSSI data.
        The rest will be parsed as a standard packet.
        :param pkt:
        :return:
        '''
        # Get the radio tap length to trim it off
        rtlen = struct.unpack('h', pkt[2:4])[0]
        ftype = (ord(pkt[rtlen]) >> 2) & 3
        stype = ord(pkt[rtlen]) >> 4

        # 0x04 - Probe Request:
        if ftype == 0 and stype == 4:
            rtap = pkt[:rtlen]
            frame = pkt[rtlen:]
            # parse transmitter address to string
            mac = frame[10:16].encode('hex')
            mac = ':'.join([mac[x:x+2] for x in xrange(0, len(mac), 2)])
            # parse rssi (from radiotap)
            rssi = struct.unpack("b", rtap[-4:-3])[0]
            # parse SSID (if not broadcast, check length and parse the string)
            ssid = frame[26:26+ord(frame[25])] if ord(frame[25]) > 0 else "<BROADCAST>"
            self.probehandler(mac, ssid, rssi)

    def run(self):
        '''
        Main process loop
        :return:
        '''
        SnifferOn = True
        self.logger.info("Locator is running...")
        while SnifferOn:
            try:
                # Grab a packet:
                (header, pkt) = self.sniffer.next()
                # Check content and parse if needed:
                if not pkt:
                    continue
                else:
                    if self.sniffer.datalink() == LINKTYPE_IEEE802_11_RADIOTAP:
                        self.packethandler(pkt)
            except KeyboardInterrupt:
                self.logger.warn("Locator interrupted. Exiting...")
                break
            except Exception as ex:
                self.logger.error("Exception in locator: %s", str(ex))
                continue


locator = locator()
locator.run()