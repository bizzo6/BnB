# https://docs.python.org/2/library/configparser.html

import ConfigParser
from os.path import join, realpath, split

# Get Conf file from this folder
path, file = split(realpath(__file__))
CONF_FILE = join(path, "bnb.conf")

# Init Config Parser
config = ConfigParser.ConfigParser()
config.read(CONF_FILE)


def getstr(section, value):
    return config.get(section, value)


def getint(section, value):
    return config.getint(section, value)

# [system]
SYSTEM_VERSION = getstr("system", "system_version")

# [notifier]
NOTIFIER_GCM_API_KEY = getstr("notifier", "notifier_gcm_api_key")

# [locator]
LOCATOR_MONITOR_INTERFACE = getstr("locator", "locator_monitor_interface")
LOCATOR_DEFAULT_CHANNEL_INT = getint("locator", "locator_default_channel_int")
LOCATOR_PCAPY_SNAPLEN_INT = getint("locator", "locator_pcapy_snaplen_int")

# [debug]
LOCATOR_TEST_MAC_1 = getstr("debug", "locator_test_mac_1")
LOCATOR_TEST_MAC_2 = getstr("debug", "locator_test_mac_2")
