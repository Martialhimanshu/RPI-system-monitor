from dyfo_mail.Mailer import Mailer
from YamJam import yamjam
from Telescope.settings import logger
from constants import TELESCOPE_URL

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
        m.send_mail("Lense Alert",alert_string,['m.himanshu@dyfolabs.com'])
    except Exception as e:
        logger.error("Exception in sending alert"+str(e))