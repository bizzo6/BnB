# -*- coding: UTF-8 -*-
'''
Created: 17/04/2016

@author: bizzo6

Module: Locator - Producer (BnB)
Description:
    The locator producer module will consume all probe information found by the locator module and produce location
    entries into the main BnB database. These entries are meant to present the time duration (entry and leaving) in
    which the MAC entity was present. One location entity, once closed and saved, will include the following info:
    - MAC address
    - Time of arrival
    - Time of leaving

'''
import logging
from json import loads
from time import sleep
import libs
from conf.configuration import *


LOCATOR_MAC_LIST = [LOCATOR_TEST_MAC_1, LOCATOR_TEST_MAC_2]

BNB_LOCATOR_SLEEP_SEC = 2

DB_TABLE_NAME = 'bnb_locator'
DB_TABLE_COLUMNS = [('mac', 'TEXT'),
                    ('entertime', 'TEXT'),
                    ('lastactivetime', 'TEXT'),
                    ('leavetime', 'TEXT'),
                    ('maxrssi','INT'),
                    ('ssidlist', 'TEXT')]


class LocatorProducer(object):
    def __init__(self):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        self.db = libs.bnbdb.bnbdb(DB_TABLE_NAME, DB_TABLE_COLUMNS)
        self.ipc = libs.bnbipc.bnbipc()

    def handle(self, probe):
        '''
        Handles a json entry of a probe request located by the locator
        Will open, update or close a location entry on the DB for the specific MAC
        :param probe:
        :return:
        '''

        probe = loads(probe)
        ts = probe['ts']
        mac = probe['mac']
        rssi = probe['rssi']
        ssid = probe['ssid']
        self.logger.debug("Probe: (%s) %s --> %s (%ddB)", ts, mac, ssid, rssi)

        # Filter out macs we are not looking for:
        if mac not in LOCATOR_MAC_LIST:
            return True

        # Check if there is an open location entity that is not timed:
        current = self.locatorCheckOpenEntry(mac, ts)

        if current:
            self.locatorUpdateEntry(current, ts, rssi)
        else:
            self.locatorCreateNewEntry(mac, ts, rssi)

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

    def locatorCreateNewEntry(self, mac, entertime, rssi):
        '''
        Note: we include leavetime value as an empty '' to indicate this is an open entry waiting to be closed.
        :param mac:
        :param entertime:
        :param rssi:
        :return:
        '''
        self.db.dbnewentry([mac, entertime, '', rssi])



    def run(self):
        '''
        Main process loop
        :return:
        '''
        self.logger.info("Locator Producer is Running. Listening for probes to produce...")
        while True:
            nextinput = self.ipc.poplocatorprobe()
            if nextinput:
                self.handle(nextinput)
            else:
                # Nothing to handle, sleep for a while...
                sleep(BNB_LOCATOR_SLEEP_SEC)

def main():

    locator_producer = LocatorProducer()

    if not locator_producer.run():
        exit(-1)
    return

if __name__ == '__main__':
    main()
