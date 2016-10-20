import logging
from os import makedirs
from os.path import exists

import libs
import sqlite3 as db

DB_PATH = 'db/'
DB_FILENAME = "bnb.db"

DB_TABLE_COLUMNS_DEFAULT = [('id', 'INT PRIMARY KEY')]


class bnbdb(object):
    def __init__(self, dbTableName = '', dbTableConfig = []):
        self.logger = logging.getLogger(libs.bnbutils.LOGGING_LOGGER_NAME)
        self.dbpath = DB_PATH + DB_FILENAME
        self.dbcon = None
        self.dbcur = None

        self.dbTableName = dbTableName
        self.dbTableConfig = dbTableConfig

        # Check for relevant folders
        if not exists(DB_PATH):
            makedirs(DB_PATH)

        # Connect to DB
        if not (self.dbconnect() and self.dbinit()):
            self.logger.error("Can't initiate db services!")
            exit(1)

    def dbinit(self):
        """
        Create a new table for this type of service and initiate it (if not exists)
        :return: True/False
        """
        try:
            sqlcommand = "CREATE TABLE IF NOT EXISTS " + self.dbTableName + self.dbgettableconfig()
            self.dbcur.execute(sqlcommand)
            self.dbcur.fetchall()
            self.dbcon.commit()
        except Exception as ex:
            self.logger.error("Exception in initiating table: %s", str(ex))
            return False
        return True

    def dbconnect(self):
        '''
        Connect to the db file and initiate all the db handlers
        :return: True if all OK, False if error
        '''
        try:
            self.dbcon = db.connect(self.dbpath, check_same_thread=False)
            # Use the row dictionary cursor
            self.dbcon.row_factory = db.Row
            self.dbcur = self.dbcon.cursor()
        except db.Error, e:
            self.logger.critical("Exception n connecting to db: %s", e.args[0])
            return False
        return True

    def dbgettableconfig(self):
        '''
        Used to parse the table config param for the creation of new tables
        :return:
        '''
        conf = "("
        for column in (DB_TABLE_COLUMNS_DEFAULT + self.dbTableConfig):
            conf += "%s %s, " % (str(column[0]), str(column[1]))
        conf = conf[:-2]
        conf += ')'
        return conf

    def dbgettablecolumns(self):
        '''
        returns a list of table columns names
        :return:
        '''
        conf = "("
        for column in self.dbTableConfig:
            conf += "%s, " % str(column[0])
        conf = conf[:-2]
        conf += ')'
        return conf

    def dbnewentry(self, values=None):
        '''
        Update the DB record with the relevant list of values
        :param id:
        :param valid:
        :param values: list of values like this: ['value1','value2','value3'....] where all values are strings and in the correct table config order
        :return:
        '''
        if values:
            sqlcommand = "INSERT INTO " + self.dbTableName + self.dbgettablecolumns() + " VALUES(" + self.parsevalues(values) + ")"
        else:
            self.logger.warning("Don't have values to insert into new DB entry")
            return False

        self.logger.debug("Executing SQL command: %s", sqlcommand)
        try:
            self.dbcur.execute(sqlcommand)
            self.dbcon.commit()
        except Exception as ex:
            self.logger.error("Exception in SQL command: %s", str(ex))
            return False
        return True


    def parsevalues(self, values):
        '''
        Used for adding a list of values to a new/updated row in the database (SQL syntax)
        :param values:
        :return:
        '''
        result = ""
        for val in values:
                result += "'%s'," % val
        result = result[:-1]
        return result


    def dbclose(self):
        '''
        Close the connection to the db file
        :return:
        '''
        try:
            self.dbcon.close()
        except Exception as ex:
            self.logger.error("Exception in closing db connection: %s", str(ex))
        return

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