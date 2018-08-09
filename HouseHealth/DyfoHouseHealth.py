import time
import datetime
from datetime import datetime as dt
from utils import get_live_astros_from_drona, convert_to_standard_datetime, \
    get_severe_quick_interrupts, make_graylog_request, getConfigValue, get_pin_statuses, get_last_healthcheck
from HealthAnalysis import HealthAnalysis
from models import House
from constants import *
from Telescope.settings import logger


class DyfoHouseHealth:

    def __init__(self, house_id):
        self.house_id = house_id
        self.astros = get_live_astros_from_drona(house_id)
        self.all_astro_wifi_disconnection = {}
        self.house_wifi_disconnections = []
        self.client_disconnections = []

    def checkHouseHealth(self, range):
        self.checkAstroRestarts(range)
        self.checkLongDisconnect()
        self.checkQuickInterrupt(range)

    def checkWifiDisconnections(self, range, astro_id=None):

        if astro_id is not None:

            query = 'HOUSE_ID:' + self.house_id + ' AND Message_ASTRO_ID:' + astro_id + ' AND ENV:PROD'

        else:
            query = 'HOUSE_ID:' + self.house_id + ' AND ENV:PROD'

        payload = {'query': query,
                   'interval': 'minute',
                   'range': range,
                   'filter': 'streams:' + ASTRO_STATS_STREAM_ID}
        wifi_data = make_graylog_request(payload, GRAYLOG_WIFI_HISTOGRAM)
        wifi_disconnections = []
        wifi_disconnection = {}
        curr_state = 1
        counter = 0
        # print(wifi_data)
        for key, val in wifi_data['results'].iteritems():
            counter += 1
            if val == 0 and curr_state != 0:
                start_counter = counter
                wifi_disconnection['epoch_from'] = key
                curr_state = 0

            if val != 0 and curr_state == 0:
                if counter - start_counter > ASTRO_WIFI_DISCONNECT_THRESHOLD:
                    wifi_disconnection['epoch_to'] = key
                    wifi_disconnection['period'] = int(wifi_disconnection['epoch_to']) - int(
                        wifi_disconnection['epoch_from'])
                    wifi_disconnection['time_to'] = (datetime.datetime.fromtimestamp(
                        int(wifi_disconnection['epoch_to'])) + datetime.timedelta(hours=5, minutes=30)).strftime(
                        TIME_FORMAT)
                    wifi_disconnection['time_from'] = (datetime.datetime.fromtimestamp(
                        int(wifi_disconnection['epoch_from'])) + datetime.timedelta(hours=5, minutes=30)).strftime(
                        TIME_FORMAT)
                    # print(wifi_disconnection)
                    wifi_disconnections.append(wifi_disconnection)
                    wifi_disconnection = {}

                curr_state = 1

        if astro_id:
            self.all_astro_wifi_disconnection[astro_id] = wifi_disconnections
            return wifi_disconnections, wifi_data['results']
        else:
            self.house_wifi_disconnections = wifi_disconnections

    def checkAstroRestarts(self, range):
        try:
            self.checkWifiDisconnections(range)
            restarts = []
            payload = {'query': 'HOUSE_ID:' + self.house_id + ' AND Message_ACTION:ASTRO_INITIATED AND ENV:PROD',
                       'range': range,
                       'fields': 'ASTRO_ID,DYFO_TIME,Message_ASTRO_SKETCH_VERSION, Message_RESTART_REASON'}

            data = make_graylog_request(payload, GRAYLOG_SEARCH_RELATIVE)
            if data == None or 'messages' not in data:
                return restarts

            for item in data['messages']:
                try:
                    message = item['message']
                    astro_id = message['ASTRO_ID']
                    restart_time = message['DYFO_TIME']
                    # sketch_version = message['Message_ASTRO_SKETCH_VERSION']

                    if astro_id not in self.astros:
                        continue
                    restart_time_obj = dt.strptime(restart_time, DYFO_TIME_FORMAT_INPUT)
                    # device_type = get_device_type(sketch_version)

                    mobile_pin_status, interrupt_pin_status = get_pin_statuses(restart_time_obj,
                                                                               self.astros[astro_id][1],
                                                                               astro_id)
                    wifi_histogram = {}
                    wifi_disconnections = []
                    # , wifi_histogram = self.checkWifiDisconnections(range, astro_id)
                    code_version = House.objects.get(house_id=self.house_id).code_version


                    if "Message_RESTART_REASON" in message:
                        reason=RESTART_REASON.get(message["Message_RESTART_REASON"],"First time up")
                        comment="Derived from astro"
                    else:
                        analysis = HealthAnalysis(restart_time_obj, wifi_histogram, wifi_disconnections,
                                                  self.house_wifi_disconnections, code_version)
                        reason, comment = analysis.analyse(astro_id, restart_time_obj)

                    restart = {}
                    restart['house_id'] = self.house_id
                    restart['astro_id'] = astro_id
                    restart['restart_time'] = restart_time_obj
                    restart['wifi_disconnections'] = wifi_disconnections
                    restart['reason'] = reason
                    restart['comment'] = comment
                    restart['mobile_pin_status'] = mobile_pin_status
                    restart['interrupt_pin_status'] = interrupt_pin_status
                    restart['device_type'] = self.astros[astro_id][1]
                    restarts.append(restart)
                except Exception as e:
                    logger.error("Exception in getting restart. Exception " + str(e))
            return restarts

        except Exception as e:
            logger.error("Exception in checking restarts. Exception" + str(e))
            raise e

    def checkLongDisconnect(self):
        # print("Long Disconnected Live Astros")
        try:
            long_disconnects = {}

            for key, val in self.astros.iteritems():
                if val[0] is not None and (dt.now() + datetime.timedelta(hours=5, minutes=30) - dt.strptime(val[0],
                                                                                                            DRONA_TIME_FORMAT)) > datetime.timedelta(
                        hours=4):
                    long_disconnects[key] = val[0]
            return long_disconnects
        except Exception as e:
            logger.error("Exception in checking long disconnect. Exception" + str(e))
            raise e

    def checkQuickInterrupt(self, range):
        try:
            interrupt_bin = {}
            counter = 0
            while (1):

                payload = {'query': 'HOUSE_ID:' + self.house_id + ' AND ENV:PROD', 'range': range,
                           'fields': 'DYFO_TIME,Message_ASTRO_ID,Message_PIN_D',
                           'filter': 'streams:' + QUICK_INTERRUPT_STREAM_ID,
                           'offset': 150 * counter}

                data = make_graylog_request(payload, GRAYLOG_SEARCH_RELATIVE)
                if data == None or 'messages' not in data or len(data['messages']) == 0:
                    break
                for element in data['messages']:
                    dyfo_time = element['message']['DYFO_TIME']
                    astro_id = element['message']['Message_ASTRO_ID']
                    pin_id = element['message']['Message_PIN_D']

                    if astro_id not in self.astros:
                        continue
                    epoch = int(time.mktime(time.strptime(dyfo_time, DYFO_TIME_FORMAT_INPUT)))
                    epoch = epoch - (epoch % int(getConfigValue(INTERRUPT_BIN_VALUE)))
                    if astro_id not in interrupt_bin:
                        interrupt_bin[astro_id] = {}
                    if pin_id not in interrupt_bin[astro_id]:
                        interrupt_bin[astro_id][pin_id] = {}

                    if epoch not in interrupt_bin[astro_id][pin_id]:
                        interrupt_bin[astro_id][pin_id][epoch] = 0

                    interrupt_bin[astro_id][pin_id][epoch] += 1
                counter += 1
            # print(interrupt_bin)
            final_interrupts = get_severe_quick_interrupts(interrupt_bin, self.astros, self.house_id)
            return final_interrupts
        except Exception as e:
            logger.error("Exception in checking quick interrupts. Exception" + str(e))
            raise e
