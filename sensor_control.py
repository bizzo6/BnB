# -*- coding: UTF-8 -*-
'''
Created: 01/05/2017

@author: bizzo6
'''
import json

from conf.configuration import *
import libs
from sensors.motioneye import meyeclient

class BnBSensorController(object):

    def __init__(self):
        # Initiate Logger:
        self.logger = libs.bnbutils.logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)

        # Initiate IPC connection:
        self.ips = libs.bnbipc.bnbipc()

        # Set Sensors list:
        self.sensors = []
        self.sensors.append(meyeclient(sensorid=0, cameraid=1))
        self.sensors.append(meyeclient(sensorid=1, cameraid=4))
        self.sensors.append(meyeclient(sensorid=2, cameraid=3))

    def sensor(self, id):
        return self.sensors[id]


    def handler(self, id, type, cmd):
        '''
        For get commands - cmd is one param name to request the value of
        for set commands - cmd is a json dictionary of param and values to be set (url encoded of course)
        :param id:
        :param cmd:
        :return:
        '''

        res = ''

        if type == 'get':
            res = {}
            res[cmd] = self.sensor(id).get(cmd)
            return res

        if type == 'set':
            jcmd = json.loads(cmd)
            for key in jcmd:
                res = self.sensor(id).set(key, jcmd[key])

        return res


# DEBUG
#
# sen = BnBSensorController()
# print sen.sensor(0).get('enabled')
# print sen.sensor(0).get('name')
# # print sen._sensor(0)
#

