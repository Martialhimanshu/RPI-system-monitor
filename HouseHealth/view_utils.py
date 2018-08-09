from serializers import RestartsSerializer, AviatorDisconnectSerializer, QuickInterruptSerializer, \
    RestartsReportSerializer
from utils import get_house_statuses_from_drona, get_start_time
from models import House, Restart, QuickInterrupt, LongDisconnect
from constants import BLACKLISTED
from DyfoHouseHealth import DyfoHouseHealth
from constants import DAY_SECONDS
from utils import update_last_update
import pandas as pd
import tempfile
from wsgiref.util import FileWrapper
import datetime
from django.http import HttpResponse
import os
from alerts import check_restart_alert, check_quick_interrupt_alert, check_long_disconnect_alert, send_alert
import pytz
from Telescope.settings import logger


def handle_UpdateRestarts(data):
    """
    Saves Restarts to DB using Deserialization
    :param data:
    :return:
    """
    try:
        restart_alerts = {}

        for data_item in data:
            rs = RestartsSerializer(data=data_item)
            if rs.is_valid():
                try:
                    rs.save()
                    rsa = check_restart_alert(rs.data)
                    if rsa is not "":
                        restart_alerts[rs.data['astro_id']] = rsa

                except Exception as e:
                    logger.info("Exception in saving" + str(e))
            else:
                logger.info("Errors in saving" + str(rs.errors))
        return restart_alerts
    except Exception as e:
        logger.error("Exception in handling restarts. Exception" + str(e))


def handle_UpdateQInterrupts(interrupts, house_id):
    """
    Saves Severe Quick Interrupts to Db
    :param interrupts:
    :param house_id:
    :return:
    """
    try:
        qi_alerts = {}
        for data_item in interrupts:
            rs = QuickInterruptSerializer(data=data_item)
            if rs.is_valid():
                try:
                    rs.save()
                    qi_alerts[rs.data['astro_id']] = check_quick_interrupt_alert(rs.data)


                except Exception as e:
                    logger.info("Exception in saving" + str(e))
            else:
                logger.info("Errors in saving" + str(rs.errors))

        return qi_alerts
    except Exception as e:
        logger.error("Exception in handling quick interrupts. Exception" + str(e))


def handle_UpdateHouse():
    """
    Updates the status as well as Counts of all attributes(restarts, long cutoff, quick interrupt) for a House.
    :return:
    """
    try:
        houses = get_house_statuses_from_drona()
        blacklisted = BLACKLISTED
        time = get_start_time()
        for house in houses:
            if house['display_id'] in blacklisted:
                continue
            try:
                h = House.objects.get(house_id=house['display_id'])
            except:
                h = House.objects.create(house_id=house['display_id'])

            if (not house['master_status']) and h.status == 'ACTIVE':
                h.status = 'ERRORED' + " " + datetime.datetime.now(pytz.timezone('Asia/Calcutta')).strftime(
                    "%Y-%m-%d %H:%M:%S")
            if house['master_status']:
                h.status = 'ACTIVE'

            h.house_name = house['name']
            h.restart_count = Restart.objects.filter(house_id=house['display_id'], restart_time__gt=time).count()
            # qis = QuickInterruptSerializer(QuickInterrupt.objects.filter(house_id=key), many=True,
            #                                context={'time_constrain': time})
            # c = 0
            # for q in qis.data:
            #     c += len(q['interrupts'])
            h.qi_count = QuickInterrupt.objects.filter(house_id=house['display_id'], time__gt=time).count()
            h.ld_count = LongDisconnect.objects.filter(house_id=house['display_id'], status="INACTIVE").count()
            h.save()
        return houses
    except Exception as e:
        logger.error("Exception in updating house information from local db. Exception" + str(e))
        raise e


def handle_UpdateLongCutoff(data, house_id):
    """
    Checks if previously Inactive astros are still Inactive or not.
    If they have reconnected, mark them as active.
    Makes DB entries for other Long Cutoffs.

    :param obj:
    :param house_id:
    :return:
    """
    try:
        ld_objects = LongDisconnect.objects.filter(house_id=house_id)
        ldo_alert = {}
        for ld in ld_objects:
            if ld.astro_id not in data:
                ld.delete()

        for key, val in data.iteritems():
            try:
                ldo = LongDisconnect.objects.get(astro_id=key)
            except:
                ldo = LongDisconnect.objects.create(house_id=house_id, astro_id=key)
                ldo_alert[key] = check_long_disconnect_alert(key, val)
            ldo.disconnected_at = val
            ldo.status = "INACTIVE"
            ldo.save()
            # ldo_alert=check_long_disconnect_alert(key, val)

        return ldo_alert
    except Exception as e:
        logger.error("Exception in updating long cut off. Exception " + str(e))


def handle_UpdateAviatorDisconnections(data):
    """
    Deserialize Aviator Disconnections to DB
    :param obj:
    :param duration:
    :return:
    """
    ad = AviatorDisconnectSerializer(data=data, many=True)

    if ad.is_valid():
        try:
            ad.save()
        except Exception as e:
            print str(e)
    else:
        return ad.errors
    return data


def get_AstroRestarts(house_id):
    time = get_start_time()

    rs = RestartsSerializer(Restart.objects.filter(house_id=house_id, restart_time__gt=time).order_by('-restart_time'),
                            many=True)

    return rs.data


def get_Quick_Interrupts(house_id):
    time = get_start_time()
    qis = QuickInterruptSerializer(QuickInterrupt.objects.filter(house_id=house_id, time__gt=time).order_by('-time'),
                                   many=True)
    return qis.data


def handle_UpdateAll():
    try:
        houses = get_house_statuses_from_drona()
        blacklisted = BLACKLISTED
        for house in houses:
            if house['display_id'] in blacklisted:
                continue
            try:
                h = House.objects.get(house_id=house['display_id'])
            except:
                h = House.objects.create(house_id=house['display_id'])

            if (not house['master_status']) and h.status == 'ACTIVE':
                h.status = 'ERRORED' + " " + datetime.datetime.now(pytz.timezone('Asia/Calcutta')).strftime(
                    "%Y-%m-%d %H:%M:%S")
            if house['master_status']:
                h.status = 'ACTIVE'
            h.code_version = house['code_version']
            h.save()
        houses = House.objects.filter(to_update=True)
        alerts = {}

        for house in houses:
            dyfo_house = DyfoHouseHealth(house.house_id)
            data = dyfo_house.checkAstroRestarts(DAY_SECONDS)
            alert = handle_UpdateRestarts(data)
            if alert:
                if house.house_id not in alerts:
                    alerts[house.house_id] = {}
                    alerts[house.house_id]['name'] = house.house_name
                alerts[house.house_id]['Restarts'] = alert

            data = dyfo_house.checkQuickInterrupt(DAY_SECONDS)
            alert = handle_UpdateQInterrupts(data, house.house_id)
            if alert:
                if house.house_id not in alerts:
                    alerts[house.house_id] = {}
                    alerts[house.house_id]['name'] = house.house_name

                alerts[house.house_id]['Quick_Interrupts'] = alert

            data = dyfo_house.checkLongDisconnect()
            alert = handle_UpdateLongCutoff(data, house.house_id)
            if alert:
                if house.house_id not in alerts:
                    alerts[house.house_id] = {}
                    alerts[house.house_id]['name'] = house.house_name
                alerts[house.house_id]['Long_Disconnect'] = alert

        if alerts:
            send_alert(alerts)

        update_last_update()
    except Exception as e:
        logger.error("Exception in updating Houses. Exception " + str(e))
        raise e


def handle_GenerateReport(house_id):
    rs = RestartsReportSerializer(Restart.objects.filter(house_id=house_id, reason='NO SOFTWARE REASON FOUND'),
                                  many=True)
    df = pd.DataFrame.from_dict(rs.data)
    tempdir = tempfile.mkdtemp()
    filepath = tempdir + '/sheet.csv'
    df.to_csv(filepath)
    with open(filepath, 'rb') as fh:
        response = HttpResponse(FileWrapper(fh), content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(filepath)
        response['Content-Length'] = os.path.getsize(filepath)
        return response
