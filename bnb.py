# -*- coding: UTF-8 -*-
'''
Created: 04/10/2015

@author: bizzo6
'''
from conf.configuration import *
import logging
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, abort, make_response, send_file
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth
from io import BytesIO
import sys
import signal
import urllib2
import libs
from sensor_control import BnBSensorController
from alarm_control import BnBAlarmController

# DEFAULT RESPONSES:
RESP_STATUS_OK = 'OK'
RESP_STATUS_NOT_OK = 'error'

# Flask Server Params:
BASIC_AUTH_USERNAME = BNB_USERNAME
BASIC_AUTH_PASSWORD = BNB_PASSWORD
DEBUG_MODE = True           # Flask debug mode
HOST_ADDRESS = '0.0.0.0'    # use 0.0.0.0 to listen to external connections
HOST_PORT = int(BNB_PORT)
HOST_SSL = False             # True to enable https, False to fallback to http
SERVER_THREADED = True     # Flask debug server in multi-threading mode
HOST_CERT_PATH = 'certs/host.cert'
HOST_KEY_PATH = 'certs/host.key'

# Flask defaults
RESPONSE_DEFAULT = {'status': RESP_STATUS_OK,
                    'data': {}}



# Initiate Values
startTime = time.time()

# Handlers and Controllers
sensors = BnBSensorController()

# Alarms
alarms = BnBAlarmController()


# Start FLASK application
app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == BASIC_AUTH_USERNAME:
        return BASIC_AUTH_PASSWORD
    return None

@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog
    #return make_response(jsonify({'message': 'Unauthorized access'}), 403)
    return make_response(jsonify({'message': 'Unauthorized access'}), 401)
    
    
class BnBStatus(Resource):
    def __init__(self):
        super(BnBStatus, self).__init__()

    @auth.login_required
    def get(self):
        res = RESPONSE_DEFAULT
        # Calculate stats:
        uptime = datetime(1, 1, 1) + timedelta(seconds=(time.time() - startTime))
        suptime = "%02d:%02d:%02d:%02d" % (uptime.day-1, uptime.hour, uptime.minute, uptime.second)
        # Set values:
        resdata = res['data']
        resdata['version'] = BNB_VERSION
        resdata['uptime'] = suptime
        return res

    def post(self):
        abort(404)

    def put(self):
        abort(404)

    def delete(self):
        abort(404)
        
class BnBSensorAPI(Resource):
    def __init__(self):
        super(BnBSensorAPI, self).__init__()

    @auth.login_required
    def get(self, id, type, cmd):
        # Default response
        res = RESPONSE_DEFAULT

        # Handle get command:
        if type == "get":
            print "Got get command"

        # Handle set command
        if type == "set":
            print "Got set"

        print cmd
        result = sensors.handler(id, type, cmd)

        return {'status': RESP_STATUS_OK,
                'data': result }

    def post(self,id):
        abort(404)

    def put(self,id):
        abort(404)

    def delete(self,id):
        abort(404)


class BnBAlarmAPI(Resource):
    def __init__(self):
        super(BnBAlarmAPI, self).__init__()

    @auth.login_required
    def get(self, cmd):
        # Default response
        res = RESPONSE_DEFAULT

        # Handle start alarm:
        if cmd == "on":
            print "Starting ALARM!"

        # Handle set command
        if cmd == "off":
            print "Stopping ALARM!"

        result = alarms.handler(cmd)

        return {'status': RESP_STATUS_OK,
                'data': result }

    def post(self, cmd):
        abort(404)

    def put(self, cmd):
        abort(404)

    def delete(self, cmd):
        abort(404)


class BnBTestAPI(Resource):
    def __init__(self):
        super(BnBTestAPI, self).__init__()

    @auth.login_required
    def get(self, id):
        response = urllib2.urlopen('http://weknowyourdreams.com/images/banana/banana-06.jpg')
        snapshot = response.read()
        return send_file(BytesIO(snapshot), attachment_filename='snapshot.jpg', mimetype='image/jpg')

    def post(self,id):
        abort(404)

    def put(self,id):
        abort(404)

    def delete(self,id):
        abort(404)
    

api.add_resource(BnBStatus,     '/status')
api.add_resource(BnBSensorAPI,  '/sensor/<int:id>/<string:type>/<string:cmd>')
api.add_resource(BnBAlarmAPI,  '/alarm/<string:cmd>')
#api.add_resource(BnBSensorAPI,  '/bnb/sensor/<int:id>')


def sigterm_handler(_signo, _stack_frame):
    print("Received signal {}, exiting...".format(_signo))
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)


def main():
    # Initiate logger:
    logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
    logger.info("Starting up")

    if HOST_SSL:
        logger.info("Running under HTTPS context")
        context = (HOST_CERT_PATH, HOST_KEY_PATH)
        app.run(debug=DEBUG_MODE, host=HOST_ADDRESS, port=HOST_PORT, ssl_context=context, threaded=SERVER_THREADED)
    else:
        logger.info("Running on clear HTTP")
        app.run(debug=DEBUG_MODE, host=HOST_ADDRESS, port=HOST_PORT, threaded=SERVER_THREADED)
    return

if __name__ == '__main__':
    main()
