# -*- coding: UTF-8 -*-
'''
Created: 17/08/2017

@author: bizzo6
'''
import os
import subprocess
import libs
from conf.configuration import *
from slackclient import SlackClient
import logging
import requests

ALARM_FILE = 'media/siren.mp3'
PLAY_CMD = 'mpg123 --loop -1 ' + ALARM_FILE

'''
NOTE! make sure to run this command:
amixer cset numid=3 1
on startup. This will make sure audio output goes to audio jack (And not HDMI or something else)

Also, set volume with this tool:
alsamixer

see: http://karuppuswamy.com/wordpress/2015/08/15/configuring-alsa-audio-output-on-analog-and-hdmi-of-raspberry-pi/

'''


TRIGGERS = [
    {'name': ALARM_TRIGGER_NAME_1,
     "notification_msg": ALARM_TRIGGER_NOTIFICATION_1,
     "snapshot_url": ALARM_TRIGGER_SNAPSHOT_URL_1
     }
]

class slackbot(object):

    def __init__(self):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        # instantiate Slack client
        self.client = SlackClient(ALARM_TRIGGER_SLACKAPI)
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

    def send_image(self, image, msg, channel):
        #with open('test.jpg', 'rb') as file_content:
        self.client.api_call(
            "files.upload",
            channels=channel,
            file=image,
            filename='test.jpg',
            filetype='jpg',
            title=msg)
        self.logger.debug("Slack Bot (%s): Uploading Image Titled %s" % (channel, msg))

class BnBAlarmController(object):

    def __init__(self):
        # Initiate Logger:
        self.logger = libs.bnbutils.logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)

        # Initiate IPC connection:
        #self.ips = libs.bnbipc.bnbipc()

        # Connect to slack bot:
        self.bot = slackbot()
        self.bot.connect()

        # Set audio output to 3.5mm jack:
        os.system('amixer cset numid=3 1')
        os.system('amixer cset numid=3 1')

        # Set Alarms File:
        self.pid = None
        self.isactive = False
        self.process = None

    def get_snapshot(self, url):
        return requests.get(url).content

    def handler(self, cmd):
        if cmd == 'on':
            if not self.isactive:
                self.logger.info("Running: %s" % PLAY_CMD)
                #self.process = subprocess.Popen(PLAY_CMD, shell=True)
                self.process = subprocess.Popen("exec " + PLAY_CMD, stdout=subprocess.PIPE, shell=True)
                self.pid = self.process.pid
                self.logger.info("Started Alarm (pid=%d)" % self.pid)
                self.isactive = True
            else:
                self.logger.warning("Doing nothing, alarm already ON!")
            return True

        if cmd == 'off':
            if self.isactive:
                self.logger.info("Stopping Alarm (pid=%d):" % self.pid)
                self.process.kill()
                #os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
                self.process = None
                self.isactive = False
            else:
                self.logger.warning("Alarms already Stopped!")
            return True

        return True

    def trigger(self, cmd):
        res = False

        for trigger in TRIGGERS:
            if cmd == trigger['name']:
                self.logger.info("Triggered %s!", trigger['name'])
                self.bot.send_msg(trigger['notification_msg'], "home")
                snapshot = self.get_snapshot(trigger['snapshot_url'])
                self.bot.send_image(snapshot, trigger['name'], "home")
                res = True
        return res
