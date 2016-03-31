# -*- coding: UTF-8 -*-
'''
Created: 04/10/2015

@author: Nati
'''

from flask import Flask, jsonify, abort, make_response, send_file
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from flask.ext.httpauth import HTTPBasicAuth

from io import BytesIO

import sys
import signal

import urllib2

# Start FLASK application
app = Flask(__name__, static_url_path="")
api = Api(app)
auth = HTTPBasicAuth()
        
@auth.get_password
def get_password(username):
    if username == 'bizzo':
        return 'bizzo'
    return None

@auth.error_handler
def unauthorized():
    # return 403 instead of 401 to prevent browsers from displaying the default
    # auth dialog
    return make_response(jsonify({'message': 'Unauthorized access'}), 403)
    
    
class BnBStatus(Resource):
    def __init__(self):
        super(BnBStatus, self).__init__()

    def get(self):
        return {'status': 'OK'}

    def post(self):
        abort(404)

    def put(self):
        abort(404)

    def delete(self):
        abort(404)
        
        
class BnBSensorAPI(Resource):
    def __init__(self):
        super(BnBSensorAPI, self).__init__()

    def get(self,id):
        response = urllib2.urlopen('https://www.organicfacts.net/wp-content/uploads/2013/05/Banana3.jpg')
        snapshot = response.read()
        return send_file(BytesIO(snapshot),attachment_filename='snapshot.jpg',mimetype='image/png')

    def post(self,id):
        abort(404)

    def put(self,id):
        abort(404)

    def delete(self,id):
        abort(404)
    

api.add_resource(BnBStatus,     '/bnb/api/v1/status/')
api.add_resource(BnBSensorAPI,  '/bnb/api/v1/sensor/<int:id>')


def sigterm_handler(_signo, _stack_frame):
    print("Received signal {}, exiting...".format(_signo))
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
    
# host='0.0.0.0' - make the app visible externally
