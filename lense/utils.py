# from models import House, AlertThreshold
# from dyfo_mail.Mailer import Mailer
# from YamJam import yamjam
# from Telescope.settings import logger
# from constants import TELESCOPE_URL
#
#
# def deleteHouse(h_id):
#     try:
#         House.objects.get(id=h_id).delete()
#         return 1
#     except:
#         return 0
#
# def send_alert(alerts):
#     try:
#         alert_string=""
#         for house, val in alerts.iteritems():
#             alert_string += "<b>"+house+"</b>"+"<br>"
#             name = val.pop('name')
#             alert_string += "<b>"+name+"</b>"+"<br>"
#
#             for type, values in val.iteritems():
#                 alert_string += "<b>"+type+"</b>"+"<br>"
#                 for astro, values2 in values.iteritems():
#                     alert_string += values2+"<br>"
#         alert_string += "Visit "+TELESCOPE_URL+" for detailed information."
#
#         user=yamjam()['keeper_user']
#         m=Mailer(user)
#         m.send_mail("Telescope Alert",alert_string,['manobhav.j@dyfolabs.com'])
#     except Exception as e:
#         logger.error("Exception in sending alert"+str(e))
#
#
# def generate_alert(data):
#     h_id = data['house_id']
#     name = data['name']
#     level = data['level']
#     time = data['time']
#     value = data['value']
#     house = House.objects.get(id=h_id).name()
#
# def checkAlertThreshold(memory,cpu,usb):
#     threshold = AlertThreshold.objects.all()
#     if memory['percent_used'] >= threshold.mem_usage:
#         generate_alert(memory['percent_used'])
#     return 1