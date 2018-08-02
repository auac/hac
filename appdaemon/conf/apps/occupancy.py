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
        self.motion_sec=self.args["motion_sec"]
        self.start_deactivate = ""
        self.wait_timeout_handle = ""
        self.utils = self.get_app("utilities")
        self.motion_timers_immediate = {}
        self.motion_listeners_trigger = {}
        
        self.register_constraint("mvt_state")

        
        # listen for door opening  
        self.log("[INITIALIZE] Door is: {}".format(self.DOOR))
        check_motion_handle = self.listen_state(self.check_motion, self.DOOR, duration = 2)
#        listener_exist = self.check_listener(check_motion_handle)

     
    def presence_activation(self, entity, attribute, old, new, kwargs):
        """
        Turn presence input_boolean to on if presence detected if input boolean is off / door is off
        """
        self.log("[PRESENCE_ACTIVATION] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))

        self.cancel_listeners()
       
        self.door_state = self.get_state(self.DOOR)
        self.ib_state = self.get_state(self.IB)
        
        if self.door_state == "off":
            self.log("[PRESENCE_ACTIVATION] Try to cancel deactivation process.")
            self.cancel_start_deactivate()
            message = "nothing" 
            if self.ib_state == "off": 
                self.log("[PRESENCE_ACTIVATION] Enter if statement to turn on {}.".format(self.IB))
                self.call_service("input_boolean/turn_on", entity_id = self.IB)
                message = "Presence activation - {} is turned on".format(self.IB)
                self.notify_slack(message)
        else: 
            message = "Activity detected by {} but {} is {} and {} is {}".format(self.friendly_name(entity), self.DOOR, self.door_state, self.IB, self.ib_state)
 
        self.log("[PRESENCE_ACTIVATION] Sending... {}".format(message))
        
        
    def check_motion(self, entity, attribute, old, new, kwargs):
        """
        When door opened, check that there is no more motion within the last 5 mins then callback presence deactivation
        When door closed, create listeners to check for motion and then callback presence activation
        """
        
        self.log("[CHECK_MOTION] entity: {}, attribute: {}, old: {} new: {}, kwargs: {}.".format(entity, attribute, old, new, kwargs))


        if new == "on" :
            self.start_deactivate = self.run_in(self.presence_deactivation, self.motion_sec + 30, entity=entity, attribute=attribute, old_state=old, new_state=new)
            self.log("[CHECK_MOTION] New is {} so initiate deactivation.".format(new))
            timer_exist = self.check_timer(self.start_deactivate)   
        elif new == "off" :
            # listen for presence activation
            self.log("[CHECK_MOTION] New is {} so listen for any activity from motion sensors.".format(new))
            self.log("[CHECK_MOTION] Presence list is: {}".format(self.args["presence_activation"]))
            for index, p in enumerate(self.args['presence_activation']):
                self.log("[CHECK_MOTION] Adding activation sensors {} to listener".format(p))
                
                p_t = p + "_trigger"
                self.motion_listeners_trigger[p_t] = self.listen_state(self.presence_activation, p, new="on", duration = 2)

#                self.motion_listeners_immediate[p_i] = self.listen_state(self.presence_activation, p, new="on", duration = 120, immediate = True)
                if index == 0:
                    p_i = p + "_immediate"
                    old_p = self.get_state(p)
                    new_p = self.get_state(p)
                    self.mvt_entity = p                  
                    self.motion_timers_immediate[p_i] = self.run_in(self.presence_activation, self.motion_sec, entity = p, 
                                           attribute = attribute, old_state = old_p, new_state = new_p, mvt_state="on")
                
        
    def presence_deactivation(self, entity, attribute, old, new, kwargs):
        """
        Turn presence input_boolean to off if presence has not been detected for x mins
        """
        self.log("[PRESENCE_DEACTIVATION] entity: {}, attribute: {}, old: {} new: {}.".format(entity, attribute, old, new))

        self.cancel_listeners()
        
        self.door_state = self.get_state(self.DOOR)
        self.ib_state = self.get_state(self.IB)
            
        if self.ib_state == "on": 
            self.call_service("input_boolean/turn_off", entity_id = self.IB)
            message = "Presence deactivation - {} is turned off".format(self.IB)
            self.notify_slack(message)
        else: 
            message = "Activity has stopped according to {} but {} is {} and {} is already {}".format(self.friendly_name(entity), self.DOOR, self.door_state, self.IB, self.ib_state)
 
        self.log("[PRESENCE_DEACTIVATION] Sending... {}".format(message))
        
    def info_listeners(self):
      
        self.log("[INFO_LISTENERS] information on listener (which checks for motion) until door is closed again.")
        
        for p_i in self.motion_timers_immediate:
            try: 
                motion_timers_immediate_exist = self.check_timer(self.motion_timers_immediate[p_i])
            except (KeyError, ValueError):    
                motion_timers_immediate_exist = False
                self.log("[INFO_LISTENERS] Exception error mt_immediate_exist for motion_timers_immediate {}".format(p_i))

        for p_t in self.motion_listeners_trigger:
            try:    
                motion_listener_trigger_exist = self.check_listener(self.motion_listeners_trigger[p_t])
            except (KeyError, ValueError):    
                motion_listener_trigger_exist = False
                self.log("[INFO_LISTENERS] Exception error ml_trigger_exist for motion_listener_trigger {}".format(p_t))

    def cancel_listeners(self):
      
        self.log("[CANCEL_LISTENERS] Cancel/reset motion listener (which checks for motion) until door is closed again.")

        self.info_listeners()
        
        for p_i in self.motion_timers_immediate:
            try:
                self.cancel_timer(self.motion_timers_immediate[p_i])
                self.log("[CANCEL_LISTENERS] Removed old motion timer immediate: {}.".format(p_i), level="ERROR")
            except KeyError:
                self.log("[CANCEL_LISTENERS] Could not remove old motion listener.", level="ERROR")

        for p_t in self.motion_listeners_trigger:                
            try:
                self.cancel_listen_state(self.motion_listeners_trigger[p_t]) 
                self.log("[CANCEL_LISTENERS] Removed old motion listener immediate: {}.".format(p_i), level="ERROR")
            except KeyError:
                self.log("[CANCEL_LISTENERS] Could not remove old motion listener.", level="ERROR")
        
        self.info_listeners()
 
    def cancel_start_deactivate(self):

        try:    
            timer_exist = self.check_timer(self.start_deactivate)
        except (KeyError, ValueError):    
            timer_exist = False
            self.log("[CANCEL_START_DEACTIVATE] Exception error timer exists")
        
        try:
            self.cancel_timer(self.start_deactivate)
            self.log("[CANCEL_START_DEACTIVATE] Try cancel START_DEACTIVATE.")
        except (KeyError, ValueError):
            self.log("[CANCEL_START_DEACTIVATE] START_DEACTIVATE could not be cancelled.", level="ERROR")
            
        try:    
            timer_exist = self.check_timer(self.start_deactivate)
        except (KeyError, ValueError):    
            timer_exist = False
            self.log("[CANCEL_START_DEACTIVATE] Exception error timer exists")
            
    def notify_slack(self, message, **kwargs):
        self.log("[NOTIFY_SLACK] entered into local notify function")
        return self.utils.notify_slack(message, **kwargs)
        
    def check_timer(self, handle):
        time, interval, kwargs = self.info_timer(handle)
        self.log("[CHECK_TIMER] {} exists. time is {}, interval is {} kwargs is {}.".format(handle, time, interval, kwargs))
        return True
        
    def check_listener(self, handle):
#        try:
        message = "LIST VARIABLES:: "
        vals = self.info_listen_state(handle)
        
        if not isinstance(vals, (list, tuple)):
            vals = [vals]
    
        for v in vals:
            message = "{} vals: {}, ".format(message, v)
            
        self.log("[CHECK_LISTENER] {} exists. {}.".format(handle, message))
        return True
#        except:
#            self.log("[CHECK_LISTENER] {} does not exists.".format(handle))
#            result = False

    def mvt_state(self, state):
        return self.utils.state_test(self.mvt_entity, state)


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
