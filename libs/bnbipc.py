import logging
import libs
import redis
from json import dumps

## http://redis.io/topics/data-types-intro

BNBIPC_QUEUE = 'BNBIPC_QUEUE'
LOCATOR_BNBIPC_QUEUE = 'bnb_locator_probes'
BNB_KEYVALUE = 'BNB_KEYVALUE'

BNB_USER_KEYNAME = "bnb_user:"

class bnbipc(object):
    def __init__(self):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        try:
            self.red = redis.Redis()
        except Exception as ex:
            self.logger.critical("Error in connecting to Redis server: %s", str(ex))
        return

    def setuser(self, userid, username, usertype, macaddress):
        userkey = BNB_USER_KEYNAME + str(userid)
        userdata = {
            'name': username,
            'type': usertype,
            'mac': macaddress
        }
        try:
            return self.red.hmset(userkey, userdata)
        except Exception as ex:
            self.logger.error("%s", str(ex))
            return False

    def getuserbyid(self, userid):
        userkey = BNB_USER_KEYNAME + str(userid)
        user = self.red.hgetall(userkey)
        return user


    def poplocatorprobe(self):
        '''
        pops top locator probe request found from the queue
        :return:
        '''
        try:
            return self.red.rpop(LOCATOR_BNBIPC_QUEUE)
        except Exception as ex:
            self.logger.error("%s", str(ex))
            return False

    def pushlocatorprobe(self, inputid):
        '''
        Push a new probe request to the locator queue list
        :param inputid: a python dictionary with probe data
        :return: True if adding a number went well
        '''
        return self.red.lpush(LOCATOR_BNBIPC_QUEUE, inputid)

    def countfetchrequets(self):
        '''
        Returns amount of currently queued fetch requests
        :return:
        '''
        return self.red.llen(BNBIPC_QUEUE)

    def getfetchqueue(self):
        '''
        Returns list of currently queued fetch requests
        :return:
        '''
        return self.red.lrange(BNBIPC_QUEUE, 0, -1)

    def getvalue(self):
        '''
        Returns if of of currently on the go fetch request. "" if nothing is in progress
        :return:
        '''
        return self.red.get(BNB_KEYVALUE)

    def setvalue(self, value=''):
        '''
        Sets current in progress fetch id. Empty "" in case there is no fetch in progress
        :param inputid:
        :return:
        '''
        self.red.set(BNB_KEYVALUE, str(value))


    def popfulllist(self):
        '''
        Pops all current error logs from the queue
        Assumptions: this is the ONLY function to pop, no one else will call the single pop function
        :return: list of error logs
        '''
        errorlog = []
        try:
            for i in range(0, self.counterrorlog()):
                errorlog.append(self.red.lpop(BNBIPC_QUEUE))
        except Exception as ex:
            self.logger.error("%s", str(ex))
            return False

        return errorlog

    def pusherrorlog(self, errorlog):
        '''
        Adds an error log to the queue
        :param errorlog: error log in string format
        :return: True if adding went well
        '''
        return self.red.rpush(BNBIPC_QUEUE, errorlog)


# DEBUG

# ipc = bnbipc()
# print ipc.setuser(1, "USER1", "Admin", LOCATOR_TEST_MAC_1)
# print ipc.setuser(2, "USER2", "User", LOCATOR_TEST_MAC_2)
# user = ipc.getuserbyid(1)
# print user['name']
# print user['type']
# print user['mac']
#
# for userkey in ipc.red.keys(BNB_USER_KEYNAME + "*"):
#     print "ID: " + userkey.split(':')[1]
#     print ipc.red.hgetall(userkey)