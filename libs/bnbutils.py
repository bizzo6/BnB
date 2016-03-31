import logging

# LOGGER
LOGGING_LOGGER_NAME = 'bnb'
LOGGING_LEVEL = logging.DEBUG
LOGGING_FORMAT = '%(asctime)s : [%(name)s] %(filename)s (%(funcName)s) : %(levelname)s : %(message)s'
logging.basicConfig(format=LOGGING_FORMAT, level=LOGGING_LEVEL)  #, filename='external.log')