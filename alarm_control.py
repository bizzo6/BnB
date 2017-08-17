# -*- coding: UTF-8 -*-
'''
Created: 17/08/2017

@author: bizzo6
'''
import os
import subprocess
import libs

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

class BnBAlarmController(object):

    def __init__(self):
        # Initiate Logger:
        self.logger = libs.bnbutils.logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)

        # Initiate IPC connection:
        #self.ips = libs.bnbipc.bnbipc()

        # Set audio output to 3.5mm jack:
        os.system('amixer cset numid=3 1')
        os.system('amixer cset numid=3 1')

        # Set Alarms File:
        self.pid = None
        self.isactive = False
        self.process = None

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
