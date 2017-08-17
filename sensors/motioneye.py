from conf.configuration import *
import libs
import hashlib
import json
import urllib
import urlparse
import re
import logging
import requests
from random import randint

# Params
SENSOR_DEFAULT_ID = 0
DEFAULT_CAMERA_ID = 0

# Signature Defaults
_SIGNATURE_REGEX = re.compile('[^a-zA-Z0-9/?_.=&{}\[\]":, _-]')
_DOUBLE_SLASH_REGEX = re.compile('//+')

class meyeclient(object):
    def __init__(self, sensorid=SENSOR_DEFAULT_ID, cameraid=DEFAULT_CAMERA_ID, host=MOTIONEYE_HOST, port=MOTIONEYE_PORT, scheme=MOTIONEYE_SCHEME, username=MOTIONEYE_USERNAME, password=MOTIONEYE_PASSWORD):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)

        # Globals
        self.id = sensorid
        self.camid = cameraid
        self.scheme = scheme
        self.port = port
        self.host = host
        self.username = username
        self.password = password

        self.baseurl = '%s://%s:%s' % (self.scheme, self.host, self.port)

    # Exports:

    def id(self):
        return self.id


    # Private:

    def _generate_random(self):
        return randint(1, 10000)

    def _signature(self, method, path, body, key):
        parts = list(urlparse.urlsplit(path))
        query = [q for q in urlparse.parse_qsl(parts[3], keep_blank_values=True) if (q[0] != '_signature')]
        query.sort(key=lambda q: q[0])
        # "safe" characters here are set to match the encodeURIComponent JavaScript counterpart
        query = [(n, urllib.quote(v, safe="!'()*~")) for (n, v) in query]
        query = '&'.join([(q[0] + '=' + q[1]) for q in query])
        parts[0] = parts[1] = ''
        parts[3] = query
        path = urlparse.urlunsplit(parts)
        path = _SIGNATURE_REGEX.sub('-', path)
        key = _SIGNATURE_REGEX.sub('-', key)

        if body and body.startswith('---'):
            body = None # file attachment

        body = body and _SIGNATURE_REGEX.sub('-', body.decode('utf8'))

        return hashlib.sha1('%s:%s:%s:%s' % (method, path, body or '', key)).hexdigest().lower()

    def request(self, url, method, data = ''):
        finalurl = url + '&_signature=' + self._signature(method, url, data, self.password)
        self.logger.debug('REQUEST: %s', finalurl)

        if method == 'GET':
            r = requests.get(finalurl)

        if method == 'POST':
            r = requests.post(finalurl, data)

        self.logger.debug('Request Response Code: %s', r.status_code)
        if r.status_code == requests.codes.ok:
            return r.text
        else:
            return False

    def camera_get_config(self, cam):
        url = self.baseurl + '/config/%d/get/?_=%s&_username=%s' % (cam, self._generate_random(), self.username)
        self.logger.info("Getting cam #%d config from meye server", cam)
        res = self.request(url, 'GET')
        if res:
            self.logger.info("Got cam #%d config successfully!", cam)
            self.logger.debug("RESPONSE: %s", res)
            return json.loads(res)
        else:
            self.logger.error("Error in getting cam #%d config!", cam)
            self.logger.debug("ERROR: %s", res)
            return False


    def camera_set_config(self, cam, configs):
        url = self.baseurl + '/config/0/set/?_=%s&_username=%s' % (self._generate_random(), self.username)
        self.logger.info("Setting cam #%d config on meye server", cam)
        configs = {str(cam): configs}
        res = self.request(url, 'POST', json.dumps(configs))
        if res:
            self.logger.info("Set cam #%d config successfully!", cam)
            return json.loads(res)
        else:
            self.logger.error("Error in setting cam #%d config!", cam)
            return False

    def camera_update_config(self, cam, configs):
        '''
        This will read current config, update relevant values, and set it back to the camera
        TBD: keep a local config for each camera so we won't need to read it on every update
        :param cam:
        :param configs:
        :return:
        '''
        # GET CONFIG
        current_config = self.camera_get_config(cam)
        if not current_config:
            self.logger.error("Error in setting camera state!")
            return False

        # UPDATE CONFIG
        for key in configs:
            self.logger.debug("Current param %s is set to %s", key, str(current_config[key]))
            self.logger.info("Setting cam #%d param %s to %s", cam, key, configs[key])
            current_config[key] = configs[key]

        # SET CONFIG
        res = self.camera_set_config(cam, current_config)
        if not res:
            self.logger.error("Error in setting camera config!")
            return False

        return True


    def get(self, param):
        '''
        Returns the value of the request param
        :param key:
        :return:
        '''
        return self.camera_get_config(self.camid)[param]

    def set(self, key, value):
        '''
        Returns the value of the request param
        :param key:
        :param value:
        :return:
        '''
        configs = {}
        configs[key] = value
        return self.camera_update_config(self.camid, configs)