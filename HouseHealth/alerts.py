from models import Restart
from utils import get_start_time
from constants import RESTART_ALERT_THRESHOLD, TELESCOPE_URL
from dyfo_mail.Mailer import Mailer
from YamJam import yamjam
from utils import getConfigValue
from constants import DATA_DISPLAY_RANGE
from Telescope.settings import logger


def check_restart_alert(rs):
    try:
        time=get_start_time()
        rscount=Restart.objects.filter(astro_id=rs['astro_id'], restart_time__gt=time).count()
        if rscount>=RESTART_ALERT_THRESHOLD:
            return str(rs["astro_id"])+ " restarted "+str(rscount)+" times in the past "+ getConfigValue(DATA_DISPLAY_RANGE)+" hours from the time of this alert.\n"
        return ""
    except Exception as e:
        logger.error("Exception in checking restart alert"+str(e))
        raise e

def check_quick_interrupt_alert(qi):
    try:
        return "Quick Interrupt Detected on Astro "+str(qi['astro_id'])+" on Pin "+str(qi['pin'])+" with count"+str(qi['count'])+".\n"
    except Exception as e:
        logger.error("Exception in checking quick interrupt alert"+str(e))
        raise e

def check_long_disconnect_alert(astro_id, disconnected_at):
    try:
        return "Long Disconnect Detected for Astro "+ astro_id+" since "+disconnected_at+".\n"
    except Exception as e:
        logger.error("Ecxeption in checking long disconnect error"+str(e))
        raise e


def send_alert(alerts):
    try:
        alert_string=""
        for house, val in alerts.iteritems():
            alert_string += "<b>"+house+"</b>"+"<br>"
            name = val.pop('name')
            alert_string += "<b>"+name+"</b>"+"<br>"

            for type, values in val.iteritems():
                alert_string += "<b>"+type+"</b>"+"<br>"
                for astro, values2 in values.iteritems():
                    alert_string += values2+"<br>"
        alert_string += "Visit "+TELESCOPE_URL+" for detailed information."

        user=yamjam()['keeper_user']
        m=Mailer(user)
        m.send_mail("Telescope Alert",alert_string,['manobhav.j@dyfolabs.com'])
    except Exception as e:
        logger.error("Exception in sending alert"+str(e))































