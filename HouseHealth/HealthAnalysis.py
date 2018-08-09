
class HealthAnalysis:

    def __init__(self, restart_time, wifi_histogram, astro_wifi_dis, home_wifi_dis, code_version):
        self.restart_time = restart_time
        self.wifi_histogram = wifi_histogram
        self.astro_wifi_dis = astro_wifi_dis
        self.home_wifi_dis = home_wifi_dis
        self.reason = ""
        self.comment = ""
        self.code_version = code_version

    def analyse(self, astro_id, restart_time_obj):
        try:
            if self.code_version != "2.0":
                self.last_healthcheck = get_last_healthcheck(astro_id, restart_time_obj)

                if self.check_powercut() or self.check_health():
                    return (self.reason, self.comment)
                else:
                    return ("INSTALLATION/LONG WAKE UP", "No Healthcheck found in 24 hours")

            else:
                self.get_last_wifi_disconnect = get_last_wifi_disconnect(astro_id, restart_time_obj)
                self.get_last_mqtt_disconnect = get_last_mqtt_disconnect(astro_id, restart_time_obj)
                if self.check_mqtt_disconnect() or self.check_wifi_disconnect():
                    return (self.reason, self.comment)
        except Exception as e:
            logger.error("Exception in analysing restart. Exception " + str(e))
            return "", ""

    def check_powercut(self):
        try:

            for disconnection in self.home_wifi_dis:
                if abs((dt.strptime(disconnection['time_to'], TIME_FORMAT) - self.restart_time).seconds) < 120:
                    self.reason = "POWER CUT"
                    self.comment = "From " + disconnection['time_from'] + " to " + disconnection['time_to']
                    return 1

            return 0
        except Exception as e:
            logger.error("Exception in checking power cut. Exception " + str(e))
            raise e

    def check_health(self):
        try:
            if self.last_healthcheck == None:
                return 0
            diff = (self.restart_time - dt.strptime(self.last_healthcheck, DYFO_TIME_FORMAT_INPUT)).seconds
            self.comment = "Last health check received at " + self.last_healthcheck
            if diff < 120:
                self.reason = "NO SOFTWARE RESTART FOUND"
                return 1

            elif diff >= 120 and diff <= 300:
                self.reason = "SOFTWARE RESTART"
                return 1
            else:
                self.reason = "MAYBE SOFTWARE RESTART"
                return 1
        except Exception as e:
            logger.error("Exception in getting healthcheck. Exception" + str(e))
            raise e

    def check_mqtt_disconnect(self):
        try:
            if self.get_last_mqtt_disconnect == None:
                return 0
            diff = (self.restart_time - dt.strptime(self.get_last_mqtt_disconnect, DYFO_TIME_FORMAT_INPUT)).seconds
            self.comment = "Last mqtt disconnect received at " + self.get_last_mqtt_disconnect
            if diff > 300:
                self.reason = "MAYBE SOFTWARE RESTART"

            elif diff <= 300:
                self.reason = "SOFTWARE RESTART"
            return 1
        except Exception as e:
            logger.error("Exception in checking mqtt disconnect. Exception" + str(e))
            raise e

    def check_wifi_disconnect(self):
        try:
            if self.get_last_wifi_disconnect == None:
                self.reason = "NO SOFTWARE RESTART FOUND"
                self.comment = "No wifi or mqtt log found"
                return 1
            diff = (self.restart_time - dt.strptime(self.get_last_wifi_disconnect, DYFO_TIME_FORMAT_INPUT)).seconds
            self.comment = "Last wifi disconnect received at " + self.get_last_wifi_disconnect
            if diff > 300:
                self.reason = "MAYBE SOFTWARE RESTART"

            elif diff <= 300:
                self.reason = "SOFTWARE RESTART"
            return 1
        except Exception as e:
            logger.error("Exception in checking wifi disconnect. Exception" + str(e))
            raise e
