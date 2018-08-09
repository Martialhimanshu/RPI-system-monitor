HOUSE_ID = 'H-4'
MQTT_STREAM_ID = '5a33b81efb89571f451797c9'
ASTRO_STATS_STREAM_ID = '5afd8f11fb89570a272dec38'
APOLLO_STREAM_ID = '5a5f5b6dfb895739b1d44e54'
QUICK_INTERRUPT_STREAM_ID = '5afd8dc4fb89570a272deaca'
DAY_SECONDS = 3600
MASTER_SERVER_URL = "https://drona.prod.dyfolabs.com"
MASTER_SERVER_PORT = 13000
GRAYLOG_SERVER_URL = 'http://logs.dyfolabs.com:9000'
AVIATOR_WIFI_DISCONNECT_THRESHOLD = 120  # signifies 2 minutes
ASTRO_WIFI_DISCONNECT_THRESHOLD = 2  # signifies 3 minutes
QUICK_INTERRUPT_THRESHOLD = 'INTERRUPT_COUNT_THRESHOLD'
INTERRUPT_BIN_VALUE = 'INTERRUPT_RANGE'
LAST_UPDATED = 'LAST_UPDATED'
DATA_DISPLAY_RANGE = 'DATA_DISPLAY_RANGE'
GRAYLOG_SEARCH_RELATIVE = '/api/search/universal/relative'
GRAYLOG_WIFI_HISTOGRAM = GRAYLOG_SEARCH_RELATIVE + '/histogram'
GRAYLOG_SEARCH_ABSOLUTE = '/api/search/universal/absolute'
TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
# TIME_FORMAT='%b-%d %I:%M:%S %p'
DYFO_TIME_FORMAT_INPUT = '%Y-%m-%d %H:%M:%S.%f'
DYFO_TIME_FORMAT_OUTPUT = '%Y-%m-%d %H:%M:%S'

DRONA_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
BLACKLISTED = ['H-4', 'H-9', 'H-8', 'H-100', 'H-11', 'H-102', 'H-101']

PINS = {'single': ['4'], 'double': ['3', '4'], 'triple': ['3', '4', '5']}
MAX_STATUS_COUNT = 2
MAX_HEALTHCHECK_COUNT = 2
RESTART_ALERT_THRESHOLD = 2
TELESCOPE_URL = "telescope.dyfolabs.com"
PI = (
    ('fresh', 'fresh'),
    ('base tested', 'base tested'),
    ('code uploaded', 'code uploaded'),
    ('appliance mounted', 'appliance mounted'),
    ('final tested', 'final tested'),
    ('live', 'live'),
    ('returned', 'returned'),
    ('testing failed', 'testing failed'),
    ('free', 'free'),
    ('extra', 'extra'),
)
AUTHORIZATION_URL = "http://13.126.155.115/authenticate/employee/"
GET_PIN_STATUS = True
LOG_LEVEL = 'ERROR'
LOG_URL = 'logs.dyfolabs.com'
LOG_PORT = 12203
SEND_GELF_LOGS = True
RESTART_REASON={'1':"NO SOFTWARE RESTART FOUND",
                '2':"LONG_MQTT_DISCONNECT",
                '3':"ONE_DAY_RESTART",
                '4':"LONG_WIFI_DISCONNECT"}