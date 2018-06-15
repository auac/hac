import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class Notifications(hass.Hass):

    def initialize(self):
        """
        Add listen states here
        """   
            
        self.LOGLEVEL=self.args["LOGLEVEL"] 
        self.utils = self.get_app("utilities")
        
        # listen to presence changes
        self.log("[INITIALIZE] Presence list is: {}".format(self.args['presence']))
        for p in self.args['presence']:
            self.log("[INITIALIZE] Adding {} to listener".format(p))
            self.listen_state(self.presence_change, p, duration = 60)


        # listen to burgular changes for different styles of reporting to 3/from 254        
        self.log("[INITIALIZE] Burgular dict is: {}".format(self.args['burgular']))
        for b, value in self.args['burgular'].items():
            self.log("[INITIALIZE] Adding {} to listener for {}".format(b, value))
            if value == 3:
                self.listen_state(self.burgular_change, b, new = str(value))
            elif value == 254:
                self.listen_state(self.burgular_change, b, old = str(value))
        
        # listen to general changes (binary, switch, light changes)
        self.log("[INITIALIZE] General list is: {}".format(self.args['general']))
        for g in self.args['general']:
            self.log("[INITIALIZE] Adding {} to listener".format(g))
            self.listen_state(self.general_change, g, old="off", new="on", duration = 2)
            self.listen_state(self.general_change, g, old="on", new="off", duration = 2) 
 
     
    def presence_change(self, entity, attribute, old, new, kwargs):
        """
        Send notifications when presence change state
        """
        self.log("[PRESENCE_CHANGE] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))
        if new == "on" : 
            msg_state = "arrived" 
        else: 
            msg_state = "left" 
        message = "{} {} home.".format(self.friendly_name(entity).replace("Presence ", "").capitalize(), msg_state)
        self.log("[PRESENCE_CHANGE] Message is... {} ".format(message))
        try:
            self.notify_slack(message, target='#warn')
            self.log("[PRESENCE_CHANGE] Sending... {}".format(message))
        except:
            self.log("[PRESENCE_CHANGE] Unable to send message. Message is {} and state is {}.".format(message, new), level="ERROR")

        
    def burgular_change(self, entity, attribute, old, new, kwargs):
        """
        Send notifications when burgular change state
        """
        self.log("[BURGULAR_CHANGE] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))
        message = "Bugular alert {}.".format(self.friendly_name(entity))
        self.log("[BURGULAR_CHANGE] Message is... {} ".format(message))

        try:
            self.notify_slack(message, target='#warn')
            self.log("[BURGULAR_CHANGE] Sending... {}".format(message))
        except:
            self.log("[BURGULAR_CHANGE] Unable to send message. Message is {} and state is {}.".format(message, new), level="ERROR")
            
        
    def general_change(self, entity, attribute, old, new, kwargs):
        """
        Send notifications when presence change state
        """
        self.log("[GENERAL_CHANGE] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))
        device_class = self.get_state(entity, attribute="device_class") or None
        self.log("[GENERAL_CHANGE] device_class: {}.".format(device_class))
        
        msg = {
                    "connectivityon" : "is connected",
                    "dooron" :  "was opened",
                    "motionon" : "Motion detected by",
                    "occupancyon" : "Occupancy detected in",
                    "openingon" : "was opened",
                    "smokeon" : "Smoke detected by",
                    "windowon" :  "was opened",
                    "connectivityoff" : "has been disconnected",
                    "dooroff" :  "was closed",
                    "occupancyoff" : "is not occupied",
                    "openingoff" : "was closed",
                    "windowoff" :  "was closed"
            }
            
        try:
            msg_key = device_class+new
            self.log("[GENERAL_CHANGE] msg key: {}.".format(msg_key))
            msg_var = msg[msg_key]  
            self.log("[GENERAL_CHANGE] msg key: {} and msg_var: {}.".format(msg_key, msg_var))
        except :
            self.log("[GENERAL_CHANGE] Error trying device class of {} and new of {}.".format(device_class, new), level="ERROR")

        
        if device_class is None:
            self.log("[GENERAL_CHANGE] ENTER IF Device class is {} and state is {}.".format(device_class, new))
            message = "{} is {}.".format(self.friendly_name(entity), new)
        elif device_class == "motion" or device_class == "smoke" or (device_class == "occupancy" and new == "on"):
            self.log("[GENERAL_CHANGE] ENTER ELIF Device class is {} and state is {}.".format(device_class, new))
            if new == "on" :
                message = "{} {}.".format(msg_var, self.friendly_name(entity))
            else:
                message = "NO MESSAGE!"
        else:
            self.log("[GENERAL_CHANGE] ENTER ELSE Device class is {} and state is {}.".format(device_class, new))
            message = "{} {}.".format(self.friendly_name(entity), msg_var)
        
        self.log("[GENERAL_CHANGE] Message is... {} ".format(message))
            
        try:
            if message != "NO MESSAGE!":
                self.notify_slack(message, entity_id=entity, device_class=device_class)
                self.log("[GENERAL_CHANGE] Sending... {}".format(message))
            else:
                pass
        except:
            self.log("[GENERAL_CHANGE] No message to send. Device class is {} and state is {}.".format(device_class, new), level="ERROR")

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
