from dateutil import tz
from datetime import datetime as dt
import urllib
import json
from collections import OrderedDict
from constants import MASTER_SERVER_URL, MASTER_SERVER_PORT, TIME_FORMAT, QUICK_INTERRUPT_THRESHOLD, GRAYLOG_SERVER_URL, \
    LAST_UPDATED, GRAYLOG_SEARCH_ABSOLUTE, PINS, MAX_STATUS_COUNT, DYFO_TIME_FORMAT_INPUT, MAX_HEALTHCHECK_COUNT, \
    ASTRO_STATS_STREAM_ID, AUTHORIZATION_URL
from RequestEndPoint.request_util import RestCall
from YamJam import yamjam
from models import Configs
import datetime
from constants import DATA_DISPLAY_RANGE, PI, GET_PIN_STATUS
import pytz
from models import House
from rest_framework import status
from dyfo_auth.Auth import Auth
from Telescope.settings import logger

drona_user = yamjam()['drona_user']

rest_call = RestCall(user_auth=drona_user)
graylog_rest_call = RestCall(user_auth={'user': 'admin', 'pass': 'graylog@2017'})


def convert_to_standard_datetime(time):
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()
    utc = dt.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return central.strftime(TIME_FORMAT)


def get_live_astros_from_drona(house_id):
    """
    Get live astros from Drona
    :param house_id:
    :return:
    """
    try:
        try:
            astro_state = House.objects.get(house_id=house_id)['astro_state']
        except:
            astro_state = 'live'

        loaded_astros = rest_call.get(
            MASTER_SERVER_URL + ":" + str(MASTER_SERVER_PORT) + "/device/astro/all?house_did=" + house_id, timeout=20)

        loaded_astros = json.loads(loaded_astros.text)
        if astro_state == "all":
            astros = {item['display_id']: [item['inactive_since'], item['type']] for item in loaded_astros if
                      item['type'] in ['single', 'double', 'triple']}
        else:
            astros = {item['display_id']: [item['inactive_since'], item['type']] for item in loaded_astros if
                      item['state'] == astro_state and item['type'] in ['single', 'double', 'triple']}

        return astros
    except Exception as e:
        logger.error("Exception while getting user defined astros type from drona. Exception " + str(e))
        raise e


def get_severe_quick_interrupts(interrupt_bin, astros, house_id):
    """

    :param interrupt_bin:
    :return:
    """
    try:
        q_interrupt = []
        for astro_id, val1 in interrupt_bin.iteritems():
            for pin_id, val2 in val1.iteritems():
                for epoch, count in val2.iteritems():
                    if count >= int(getConfigValue(QUICK_INTERRUPT_THRESHOLD)):
                        mobile_pin_status, interrupt_pin_status = get_pin_statuses(
                            datetime.datetime.fromtimestamp(int(epoch)), astros[astro_id][1], astro_id)
                        q_interrupt.append({'astro_id': astro_id, 'house_id': house_id,
                                            'time': datetime.datetime.fromtimestamp(int(epoch)), 'pin': pin_id,
                                            'count': count, 'mobile_pin_state': mobile_pin_status.pop(str(pin_id), {}),
                                            'other_mobile_pin_state': mobile_pin_status,
                                            'interrupt_pin_state': interrupt_pin_status.pop(str(pin_id), {}),
                                            'other_interrupt_pin_state': interrupt_pin_status})

        return q_interrupt
    except Exception as e:
        logger.error("Exception in extracting severe quick interrupts from interrupt bin. Exception " + str(e))
        raise e


def make_graylog_request(payload, uri):
    """

    :param payload:
    :param uri:
    :return:

    """
    try:
        url = GRAYLOG_SERVER_URL + uri + "?{}".format(urllib.urlencode(payload))
        response = graylog_rest_call.get(url, retry=True, headers={'Accept': 'application/json'}, timeout=5)
        return json.loads(response.text, object_pairs_hook=OrderedDict)
    except Exception as e:
        logger.error("Exception in making graylog request. Exception " + str(e))
        raise e


def getConfigValue(key):
    """
    Get Configuration value from Db
    :param key:
    :return:
    """
    try:
        c = Configs.objects.get(key=key)
        return c.value
    except Exception as e:
        logger.error("Exception in getting config value of " + key + "from Database. Exception " + str(e))


def get_house_statuses_from_drona():
    """
    Status of master from Drona
    :return:
    """
    try:
        houses = rest_call.get(
            MASTER_SERVER_URL + ":" + str(MASTER_SERVER_PORT) + "/house/all", timeout=20)
        houses = json.loads(houses.text)
        return houses
    except Exception as e:
        logger.error("Exception in getting House Status from Drona. Exception " + str(e))


def get_start_time():
    """
    Returns time based on Dispaly interval defined in Db
    :return:
    """
    try:
        return datetime.datetime.now() + datetime.timedelta(hours=5) - datetime.timedelta(
            hours=int(getConfigValue(DATA_DISPLAY_RANGE)))
    except Exception as e:
        logger.error("Exception in getting start time for event according to user defined display range" + str(e))


def update_last_update():
    """
    Updates the Last Updates attribute in Db
    :return:
    """
    try:
        c = Configs.objects.get(key=LAST_UPDATED)
        c.value = datetime.datetime.now(pytz.timezone('Asia/Calcutta')).strftime("%Y-%m-%d %H:%M:%S")
        c.save()
    except Exception as e:
        logger.error("Exception in updating last updated time. Exception " + str(e))
        raise e


def get_pin_status_mobile_call(astro_id, pin_id, restart_time):
    try:
        count = 0
        while count < MAX_STATUS_COUNT:
            count += 1
            time_from = dt.strftime(restart_time - datetime.timedelta(hours=count * 20), TIME_FORMAT)
            time_to = dt.strftime(restart_time, TIME_FORMAT)

            payload = {
                'query': 'Message_ACTION:CHANGE_DEVICE_STATUS AND ASTRO_ID:' + astro_id + ' AND Message_PIN_ID:' + pin_id + ' AND ENV:PROD',
                'from': time_from,
                'to': time_to,
                'fields': 'DYFO_TIME,Message_NEW_STATUS'}
            data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)
            if data['total_results'] > 0:
                return {'mobile_call_time': data['messages'][0]['message']['DYFO_TIME'],
                        'pin_status': data['messages'][0]['message']['Message_NEW_STATUS']}
        return {'mobile_call_time': 'Not Found', 'pin_status': 'Not Found'}
    except Exception as e:
        logger.error("Exeption in getting Mobile Pin statuses" + str(e))


def get_pin_status_interrupt(astro_id, pin_id, restart_time):
    try:
        count = 0
        while count < MAX_STATUS_COUNT:
            count += 1
            time_from = dt.strftime(restart_time - datetime.timedelta(hours=count * 20), TIME_FORMAT)
            time_to = dt.strftime(restart_time, TIME_FORMAT)

            payload = {
                'query': 'Message_INTERRUPT_DETECTED_pi_id:' + astro_id + ' AND ENV:PROD AND (Message_INTERRUPT_DETECTED_pins_statuses:\"{status=1, pin_id=' + pin_id + '}\" OR Message_INTERRUPT_DETECTED_pins_statuses:\"{status=0, pin_id=' + pin_id + '}\")',
                'from': time_from,
                'to': time_to,
                'fields': 'DYFO_TIME,Message_INTERRUPT_DETECTED_pins_statuses'}
            data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)
            if data['total_results'] > 0:
                return {'interrupt_call_time': data['messages'][0]['message']['DYFO_TIME'], 'pin_status':
                    str(data['messages'][0]['message']['Message_INTERRUPT_DETECTED_pins_statuses']).split(',')[0].split(
                        '=')[1]}

        return {'interrupt_call_time': 'Not Found', 'pin_status': 'Not Found'}
    except Exception as e:
        logger.error("Exception in getting Interrupt Pin statuses" + str(e))
        raise e


def get_pin_statuses(restart_time, device_type, astro_id):
    interrupt_pin_statuses = {}
    mobile_pin_statuses = {}
    if GET_PIN_STATUS:
        for pin_id in PINS[device_type]:
            interrupt_pin_statuses[pin_id] = get_pin_status_interrupt(astro_id, pin_id, restart_time)
            mobile_pin_statuses[pin_id] = get_pin_status_mobile_call(astro_id, pin_id, restart_time)

    return mobile_pin_statuses, interrupt_pin_statuses


def get_last_healthcheck(astro_id, restart_time):
    try:
        count = 0
        while count < MAX_HEALTHCHECK_COUNT:
            count += 1
            time_from = dt.strftime(restart_time - datetime.timedelta(hours=count * 12), TIME_FORMAT)
            time_to = dt.strftime(restart_time, TIME_FORMAT)

            payload = {'query': 'Message_ASTRO_ID:' + astro_id + ' AND ENV:PROD',
                       'from': time_from,
                       'to': time_to,
                       'fields': 'DYFO_TIME',
                       'filter': 'streams:' + ASTRO_STATS_STREAM_ID}
            healthcheck_data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)
            if healthcheck_data['total_results'] > 0:
                return healthcheck_data['messages'][0]['message']['DYFO_TIME']
        return None
    except Exception as e:
        logger.error("Exception in getting last helathcheck of astro from Graylog. Exception " + str(e))
        raise e


def get_last_wifi_disconnect(astro_id, restart_time):
    try:
        time_from = dt.strftime(restart_time - datetime.timedelta(hours=12), TIME_FORMAT)
        time_to = dt.strftime(restart_time, TIME_FORMAT)

        payload = {
            'query': 'Message_ASTRO_ID:' + astro_id + ' AND ENV:PROD AND Message_ACTION:ASTRO_ALERT AND Message_STATUS:Connected',
            'from': time_from,
            'to': time_to,
            'fields': 'DYFO_TIME'
        }
        reconnect_log_data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)
        payload = {
            'query': 'Message_ASTRO_ID:' + astro_id + ' AND ENV:PROD AND Message_ACTION:ASTRO_ALERT AND Message_STATUS:Disconnected',
            'from': time_from,
            'to': time_to,
            'fields': 'DYFO_TIME'
        }
        disconnect_log_data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)

        if disconnect_log_data['total_results'] > 0:
            if reconnect_log_data['total_results'] == 0 or dt.strptime(
                    disconnect_log_data['messages'][0]['message']['DYFO_TIME'],
                    DYFO_TIME_FORMAT_INPUT) > dt.strptime(
                reconnect_log_data['messages'][0]['message']['DYFO_TIME'], DYFO_TIME_FORMAT_INPUT):
                return disconnect_log_data['messages'][0]['message']['DYFO_TIME']
            elif (restart_time - dt.strptime(
                    reconnect_log_data['messages'][0]['message']['DYFO_TIME'], DYFO_TIME_FORMAT_INPUT)).seconds < 60:
                return disconnect_log_data['messages'][0]['message']['DYFO_TIME']

        return None
    except Exception as e:
        logger.error("Exception in getting last wifi disconnect from Graylog")
        raise e


def get_last_mqtt_disconnect(astro_id, restart_time):
    try:
        time_from = dt.strftime(restart_time - datetime.timedelta(hours=12), TIME_FORMAT)
        time_to = dt.strftime(restart_time, TIME_FORMAT)

        payload = {'query': 'Message_ASTRO_ID:' + astro_id + ' AND ENV:PROD AND Message_ACTION:ASTRO_MQTT_RECONNECTED',
                   'from': time_from,
                   'to': time_to,
                   'fields': 'DYFO_TIME, Message_RECONNECTED_AT'
                   }
        reconnect_log_data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)
        payload = {'query': 'Message_ASTRO_ID:' + astro_id + ' AND ENV:PROD AND Message_ACTION:ASTRO_MQTT_DISCONNECTED',
                   'from': time_from,
                   'to': time_to,
                   'fields': 'DYFO_TIME, Message_DISCONNECTED_AT'
                   }
        disconnect_log_data = make_graylog_request(payload, GRAYLOG_SEARCH_ABSOLUTE)

        if disconnect_log_data['total_results'] > 0:
            if reconnect_log_data['total_results'] == 0 or dt.strptime(
                    disconnect_log_data['messages'][0]['message']['Message_DISCONNECTED_AT'],
                    DYFO_TIME_FORMAT_INPUT) > dt.strptime(
                reconnect_log_data['messages'][0]['message']['Message_RECONNECTED_AT'], DYFO_TIME_FORMAT_INPUT):
                return disconnect_log_data['messages'][0]['message']['Message_DISCONNECTED_AT']
        return None
    except Exception as e:
        logger.error("Exception in getting last mqtt disconnect from Graylog")
        raise e


def get_astro_states():
    try:
        drona_states = get_astro_states_from_drona()
    except:
        drona_states = PI
    states = [state[1] for state in drona_states]
    states.append('all')
    return states


def get_astro_states_from_drona():
    try:
        res = rest_call.get(
            MASTER_SERVER_URL + ":" + str(MASTER_SERVER_PORT) + "/device/astro_state_choices", timeout=20)
        return json.loads(res.text)["choices"]
    except Exception as e:
        logger.error("Exception in getting astro states choice list from Drona. Exception " + str(e))
        raise e


def authorization(email):
    try:
        a = Auth()
        return a.authenticate(email, 'telescope')
    except Exception as e:
        logger.error("Exception in authorization. Exception" + str(e))
        raise e
