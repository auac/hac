import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class WhichAircon(hass.Hass):

    def initialize(self):
        """
        Add listen states here
        """   
            
        self.LOGLEVEL=self.args["LOGLEVEL"] 
        self.DINING=self.args["DINING"]
        self.LIVING=self.args["LIVING"]
        self.IB_DINING=self.args["IB_DINING"]
        self.IB_LIVING=self.args["IB_LIVING"]
        
        runtime = datetime.time(22, 5, 0)

        self.utils = self.get_app("utilities")
        self.ac_living = self.get_app("ac_living")
        self.ac_dining = self.get_app("ac_dining")

        self.motion_listeners_immediate = {}
        self.motion_listeners_trigger = {}

        # listen for door opening  
        self.log("[INITIALIZE] Dining is: {}".format(self.DINING))
        self.log("[INITIALIZE] Living is: {}".format(self.LIVING))

        self.listen_state(self.compare_hours, self.DINING)
        self.listen_state(self.compare_hours, self.LIVING)

        self.run_daily(self.ac_living.turn_off_aircon, runtime)
        self.run_daily(self.ac_dining.turn_off_aircon, runtime)

        
    def compare_hours(self, entity, attribute, old, new, kwargs):
        """
        When door opened, check that there is no more motion within the last 5 mins then callback presence deactivation
        When door closed, create listeners to check for motion and then callback presence activation
        """
        self.log("[COMPARE_HOURS] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))

        self.dining_hours = float(self.get_state(self.DINING))
        self.living_hours = float(self.get_state(self.LIVING))
        self.ib_dining_state = self.get_state(self.IB_DINING)
        self.ib_living_state = self.get_state(self.IB_LIVING)
        
        self.log("{} had {}hrs and {} had {}hrs.".format(self.friendly_name(self.DINING),self.dining_hours,self.friendly_name(self.LIVING),self.living_hours))
        if self.dining_hours - self.living_hours >= 2:
            if self.ib_dining_state == "on" :
                self.call_service("input_boolean/turn_off", entity_id = self.IB_DINING)
                kwargs = {}
                self.ac_dining.turn_off_aircon(kwargs)
            if self.ib_living_state == "off" :
                self.call_service("input_boolean/turn_on", entity_id = self.IB_LIVING)
            self.log("[COMPARE_HOURS] Dining hours greater than Living hours so turn off / on dining / living input_boolean")
        elif self.ib_living_state - self.dining_hours >=2 :
                self.call_service("input_boolean/turn_off", entity_id = self.IB_LIVING)
                kwargs = {}
                self.ac_dining.turn_off_aircon(kwargs)
            if self.ib_dining_state == "off" :
                self.call_service("input_boolean/turn_on", entity_id = self.IB_DINING)
            self.log("[COMPARE_HOURS] Living hours greater than Dining hours so turn off / on living / dining input_boolean")

            

            
    def notify_slack(self, message, **kwargs):
        self.log("[NOTIFY_SLACK] entered into local notify function")
        return self.utils.notify_slack(message, **kwargs)

                
    def log(self,message,level="INFO"):
        """
        modifies log function
        """
        levels = {
              "CRITICAL": 50,
              "ERROR": 40,
              "WARNING": 30,
              "INFO": 20,
              "DEBUG": 10,
              "NOTSET": 0
            }
        if hasattr(self, "LOGLEVEL"):
            if levels[level]>=levels[self.LOGLEVEL]:
                super().log("{} - {}".format(level,message))
        else:
            super().log("{}".format(message),level)
