import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class Occupancy(hass.Hass):

    def initialize(self):
        """
        Add listen states here
        """   
            
        self.LOGLEVEL=self.args["LOGLEVEL"] 
        self.DOOR=self.args["door"]
        self.IB=self.args["IB"]
        self.wait_handle = ""
        self.wait_timeout_handle = ""
        self.WAIT_ENTITY=self.args["wait_entity"]
        self.utils = self.get_app("utilities")
        self.motion_listeners_immediate = {}
        self.motion_listeners_trigger = {}
        
        # listen for door opening  
        self.log("[INITIALIZE] Door is: {}".format(self.DOOR))
        check_motion_handle = self.listen_state(self.check_motion, self.DOOR, duration = 2)
#        listener_exist = self.check_listener(check_motion_handle)

     
    def presence_activation(self, entity, attribute, old, new, kwargs):
        """
        Turn presence input_boolean to on if presence detected if input boolean is off / door is off
        """
        self.log("[PRESENCE_ACTIVATION] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))
        
        self.door_state = self.get_state(self.DOOR)
        self.ib_state = self.get_state(self.IB)
        
        self.cancel_listener_timer()
           
        if self.door_state == "off" and self.ib_state == "off": 
            self.call_service("input_boolean/turn_on", entity_id = self.IB)
            message = "Activity detected by {} and {} is {} so {} is turned on".format(self.friendly_name(entity), self.DOOR, self.door_state, self.IB)
        else: 
            message = "Activity detected by {} but {} is {} and {} is {}".format(self.friendly_name(entity), self.DOOR, self.door_state, self.IB, self.ib_state)
 
        self.notify_slack(message)
        self.log("[PRESENCE_ACTIVATION] Sending... {}".format(message))
        
        
    def check_motion(self, entity, attribute, old, new, kwargs):
        """
        When door opened, check that there is no more motion within the last 5 mins then callback presence deactivation
        When door closed, create listeners to check for motion and then callback presence activation
        """
        
        self.log("[CHECK_MOTION] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))
        if new == "on" :
            self.wait_handle = self.listen_state(self.presence_deactivation, self.WAIT_ENTITY, new="off", duration = 10, immediate=True)
            self.log("[CHECK_MOTION] New is {} so listen for everyone to leave room.".format(new))

            self.log("[CHECK_MOTION] Setup wait timeout timer for 1 hour. After 1 hour of activity then assume there is still presence.".format(new))
            self.wait_timeout_handle = self.run_in(self.cancel_wait, 3600)            

        elif new == "off" :
            # listen for presence activation
            self.log("[CHECK_MOTION] New is {} so listen for any activity from motion sensors.".format(new))
            self.log("[CHECK_MOTION] Presence list is: {}".format(self.args["presence_activation"]))
            for p in self.args['presence_activation']:
                self.log("[CHECK_MOTION] Adding activation sensors {} to listener".format(p))
                p_i = p + "_immediate"
                self.motion_listeners_immediate[p_i] = self.listen_state(self.presence_activation, p, new="on", duration = 120, immediate = True)
                p_t = p + "_trigger"
                self.motion_listeners_trigger[p_t] = self.listen_state(self.presence_activation, p, new="on", duration = 2)

        
    def presence_deactivation(self, entity, attribute, old, new, kwargs):
        """
        Turn presence input_boolean to off if presence has not been detected for x mins
        """
        self.log("[PRESENCE_DEACTIVATION] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))
        
        self.door_state = self.get_state(self.DOOR)
        self.ib_state = self.get_state(self.IB)

        self.cancel_listener_timer()
            
        if self.ib_state == "on": 
            self.call_service("input_boolean/turn_off", entity_id = self.IB)
            message = "Activity has stopped according to {} and {} is {} so {} is turned off".format(self.friendly_name(entity), self.DOOR, self.door_state, self.IB)
        else: 
            message = "Activity has stopped according to {} but {} is {} and {} is {}".format(self.friendly_name(entity), self.DOOR, self.door_state, self.IB, self.ib_state)
 
        self.notify_slack(message)
        self.log("[PRESENCE_DEACTIVATION] Sending... {}".format(message))
        
    def info_listener_timer(self):
      
        self.log("[INFO_LISTENER_TIMER] information on listener (which checks for motion) until door is closed again.")

        try:    
            listener_exist = self.check_listener(self.wait_handle)
        except (KeyError, ValueError):    
            listener_exist = False
            self.log("[INFO_LISTENER_TIMER] Exception error listener_exist for wait_handle {}".format(self.wait_handle))
     
        try:    
            timer_exist = self.check_timer(self.wait_timeout_handle)
        except (KeyError, ValueError):    
            timer_exist = False
            self.log("[INFO_LISTENER_TIMER] Exception error timer_exist for wait_timeout_handle {}".format(self.wait_timeout_handle))
        
        for p in self.args['presence_activation']:
            try: 
                p_i = p + "_immediate"
                motion_listener_immediate_exist = self.check_listener(self.motion_listeners_immediate[p_i])
            except (KeyError, ValueError):    
                motion_listener_immediate_exist = False
                self.log("[INFO_LISTENER_TIMER] Exception error ml_immediate_exist for motion_listener_immediate {}".format(self.motion_listeners_immediate[p_i]))

            try:    
                p_t = p + "_trigger"
                motion_listener_trigger_exist = self.check_listener(self.motion_listeners_trigger[p_t])
            except (KeyError, ValueError):    
                motion_listener_trigger_exist = False
                self.log("[INFO_LISTENER_TIMER] Exception error ml_trigger_exist for motion_listener_trigger {}".format(self.motion_listeners_immediate[p_t]))

    def cancel_listener_timer(self):
      
        self.log("[CANCEL_LISTENER_TIMER] Cancel/reset motion listener (which checks for motion) until door is closed again.")

        self.info_listener_timer()
        
        try:
            self.cancel_listen_state(self.wait_handle)
            self.log("[CANCEL_LISTENER_TIMER] Cancel/reset wait listener (which checks for no more motion) until door is opened again.")
        except KeyError:
            self.log("[CANCEL_LISTENER_TIMER] Could not remove old wait listener.", level="ERROR")

        try:
            self.cancel_timer(self.wait_timeout_handle)
            self.log("[CANCEL_LISTENER_TIMER] Remove any old wait timeout timer.")
        except KeyError:
            self.log("[CANCEL_LISTENER_TIMER] Could not remove old wait timeout timer.", level="ERROR")
        
        for p in self.args['presence_activation']:
            try:
                p_i = p + "_immediate"
                self.cancel_listen_state(self.motion_listeners_immediate[p_i])
            except KeyError:
                self.log("[CANCEL_LISTENER_TIMER] Could not remove old motion listener.", level="ERROR")
                
            try:
                p_t = p + "_trigger"
                self.cancel_listen_state(self.motion_listeners_trigger[p_t]) 
            except KeyError:
                self.log("[CANCEL_LISTENER_TIMER] Could not remove old motion listener.", level="ERROR")
        
        self.info_listener_timer()
 
    def cancel_wait(self, kwargs):

        try:    
            listener_exist = self.check_listener(self.wait_handle)
        except (KeyError, ValueError):    
            listener_exist = False
            self.log("[CANCEL_WAIT] Exception error listener_exist")
        
        try:
            self.cancel_listen_state(self.wait_handle)
            self.log("[CANCEL_WAIT] Try cancel wait as there is still motion after door opened.")
        except (KeyError, ValueError):
            self.log("[CANCEL_WAIT] Wait could not be cancelled.", level="ERROR")
            
    def notify_slack(self, message, **kwargs):
        self.log("[NOTIFY_SLACK] entered into local notify function")
        return self.utils.notify_slack(message, **kwargs)
        
    def check_timer(self, handle):
        time, interval, kwargs = self.info_timer(handle)
        self.log("[CHECK_TIMER] {} exists. time is {}, interval is {} kwargs is {}.".format(handle, time, interval, kwargs))
        return True
        
    def check_listener(self, handle):
#        try:
        vals = self.info_listen_state(handle)
        self.log("[CHECK_LISTENER] {} exists. entity is {}.".format(handle, vals[1]))
        return True
#        except:
#            self.log("[CHECK_LISTENER] {} does not exists.".format(handle))
#            result = False


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
