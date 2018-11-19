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
            self.log("[INITIALIZE] Adding {} to listener now".format(p))
            d, e = self.split_entity(p)
            if d == "binary_sensor": seconds=120 
            else: seconds=30
            self.listen_state(self.presence_change, p, new="on", duration = seconds, immediate= True)
            self.listen_state(self.presence_change, p, new="off", duration = seconds, immediate= True)
            new_state = self.utils.entity_state(p)
            self.update_device_tracker(p, new_state)

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
        
        
        message, updated = self.update_device_tracker(entity, new)

        self.log("[PRESENCE_CHANGE] Message is... {} and updated is {}.".format(message, updated))
        
        if updated is True:
            try:
                self.notify_slack(message, target='#warn')
                self.log("[PRESENCE_CHANGE] Sending... {}".format(message))
            except:
                self.log("[PRESENCE_CHANGE] Unable to send message. Message is {} and state is {}.".format(message, new), level="ERROR")		

    
    def update_device_tracker(self, entity, new):
    
        updated = True

        d, e = self.split_entity(entity)
        desc_name = self.friendly_name(entity).replace("Presence ", "")

        if new == "on": 
            msg_state = "arrived" 
            new_dt_state = "home"

        else: 
            msg_state = "left" 
            new_dt_state = "not_home"
     
        if d == "binary_sensor":
            dt_sensor_source = "_bayesian"   
        else:
            dt_sensor_source = "_homekit"     
 
        
        if desc_name != "General":  

            new_entity_id = "device_tracker.{}{}".format(e,dt_sensor_source)         
            current_dt_state = self.utils.entity_state(new_entity_id)
            
            self.log("[UPDATE_DEVICE_TRACKER] Device tracker: {} current state is {} and required state is {} ".format(new_entity_id, current_dt_state, new_dt_state))
            
            if current_dt_state != new_dt_state:
                self.log("[UPDATE_DEVICE_TRACKER] ENTER IF Device tracker: {} current state is {} and required state is {} ".format(new_entity_id, current_dt_state, new_dt_state))

                self.call_service("device_tracker/see", dev_id= e + dt_sensor_source, 
                                  location_name = new_dt_state)
                self.log("[UPDATE_DEVICE_TRACKER] Device tracker updated for {} ".format(entity))
                self.log("[UPDATE_DEVICE_TRACKER] Device tracker updated for {} ".format(new_entity_id))
                new_state = self.utils.entity_state(new_entity_id)
                self.log("[UPDATE_DEVICE_TRACKER] Device tracker new state is {} ".format(new_state)) 
            else:
                updated = False      
              
 
        message = "{} {} home. Entity_id: {}".format(desc_name, msg_state, entity)
 
        return message, updated
        
            
        
        
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
                    "connectivityon" : ["is connected","last"],
                    "dooron" :  ["was opened","last"],
                    "motionon" : ["Motion detected by","first"],
                    "occupancyon" : ["Occupancy detected in","first"],
                    "openingon" : ["was opened","last"],
                    "presenceon" : ["Presence detected in","first"],
                    "smokeon" : ["Smoke detected by","first"],
                    "windowon" :  ["was opened","last"],
                    "connectivityoff" : ["has been disconnected","last"],
                    "dooroff" :  ["was closed","last"],
                    "occupancyoff" : ["is not occupied","last"],
                    "openingoff" : ["was closed","last"],
                    "presenceoff" : ["is not detected","last"],
                    "windowoff" :  ["was closed","last"]
            }


        try: 
            if device_class == "None" or device_class is None:
                self.log("[GENERAL_CHANGE] ENTER IF Device class is None and state is {}.".format(new))
                message = "{} is {}.".format(self.friendly_name(entity), new)
            else:
                msg_key = device_class+new
                self.log("[GENERAL_CHANGE] msg key: {}.".format(msg_key))
                msg_var = msg[msg_key][0]
                msg_seq = msg[msg_key][1]
                self.log("[GENERAL_CHANGE] msg key: {} and msg_var: {}.".format(msg_key, msg_var))          
                                
                if msg_seq == "first" :   
                    self.log("[GENERAL_CHANGE] ENTER IF Device class is {} and state is {}.".format(device_class, new))
                    message = "{} {}.".format(msg_var, self.friendly_name(entity))
                else:
                    self.log("[GENERAL_CHANGE] ENTER ELIF Device class is {} and state is {}.".format(device_class, new))
                    message = "{} {}.".format(self.friendly_name(entity), msg_var)                    


            self.log("[GENERAL_CHANGE] Message is... {} ".format(message))
            self.notify_slack(message, entity_id=entity, device_class=device_class)
            self.log("[GENERAL_CHANGE] Sending... {}".format(message))

        except :
            msg_var = None
            self.log("[GENERAL_CHANGE] EXCEPT Error trying device class of {} and new of {}. msg_var: {}".format(device_class, new, msg_var))
            self.log("[GENERAL_CHANGE] EXCEPT No message to send. Device class is {} and state is {}.".format(device_class, new))


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
