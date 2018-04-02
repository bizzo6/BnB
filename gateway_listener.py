# -*- coding: UTF-8 -*-
'''
Created: 10/04/2016

@author: bizzo6

Module: Gateway Listener (BnB)
Description:
    Listens to UDP broadcast on port 9898

'''
import logging
import socket
import json
import re
from slackclient import SlackClient

from conf.configuration import *
import struct
import libs
from datetime import datetime

MCAST_PORT = 9898
BUFFER_SIZE = 1024
MCAST_ADDRESS = "224.0.0.50"

# SENSORS:
DOORS = [
    {'sid': GATEWAY_LISTENER_SID_1, 'status_to_trigger': "open", "notification_msg": "Storage Room Door is OPEN!"},
    {'sid': GATEWAY_LISTENER_SID_2, 'status_to_trigger': "open", "notification_msg": "Front Door is OPEN!"},
    {'sid': GATEWAY_LISTENER_SID_3, 'status_to_trigger': "open", "notification_msg": "Balcony is OPEN!"}
]



class slackbot(object):

    def __init__(self):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        # instantiate Slack client
        self.client = SlackClient(GATEWAY_LISTENER_SLACKAPI)
        # starterbot's user ID in Slack: value is assigned after the bot starts up
        self.starterbot_id = None


    def connect(self):
        if self.client.rtm_connect(with_team_state=False):
            self.logger.info("Starter Bot connected and running!")
            # Read bot's user ID by calling Web API method `auth.test`
            self.starterbot_id = self.client.api_call("auth.test")["user_id"]
        else:
            self.logger.error("Connection failed. Exception traceback printed above.")

    def send_msg(self, msg, channel):
        self.client.api_call(
            "chat.postMessage",
            channel=channel,
            text=msg)
        self.logger.debug("Slack Bot (%s): %s" % (channel, msg))


class listener(object):

    def __init__(self, port=MCAST_PORT, buffsize=BUFFER_SIZE, addr=MCAST_ADDRESS):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        self.ipc = libs.bnbipc.bnbipc()
        self.port = port
        self.addr = addr
        self.bufferSize = buffsize

        # Init Socket for listening

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', self.port))    # use MCAST_GRP instead of '' to listen only
                                            # to MCAST_GRP, not all groups on MCAST_PORT
        mreq = struct.pack("4sl", socket.inet_aton(self.addr), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)


    def jsonget(self, obj, key):
        if key in obj:
            return obj[key]
        else:
            return False

    def run(self, bot):
        '''
        Main process loop
        :return:
        '''

        while True:
            data = self.sock.recv(self.bufferSize)
            self.logger.debug(data)

            packet = json.loads(data)
            sid = packet['sid']
            for trigger in DOORS:
                if sid == trigger['sid']:
                    packetdata = json.loads(self.jsonget(packet, 'data'))
                    if trigger['status_to_trigger'] == self.jsonget(packetdata, 'status'):
                        bot.send_msg(trigger['notification_msg'], "home")

# Connect to slack:
bot = slackbot()
bot.connect()

listener = listener()
listener.run(bot)



