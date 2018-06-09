import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class Aircon(hass.Hass):

  def initialize(self):
     self.utils = self.get_app("utilities")

     self.temperature_id = self.args["temperature_id"]
     self.humidity_id = self.args["humidity_id"]
     self.occupancy_id = self.args["occupancy_id"]
     self.climate_id = self.args["climate_id"]
     self.binary_reverse = self.args["binary_reverse"]
     
     self.LOGLEVEL=self.args["LOGLEVEL"]

     self.register_constraint("occupancy_test")
     self.register_constraint("fan_test")
     self.register_constraint("climate_state")
     self.register_constraint("check_timer")
     
     self.listen_state(self.temp_change, self.temperature_id, duration = 30)
     self.listen_state(self.occupancy_change, self.occupancy_id, new="on", duration = 30, immediate=True)
     self.listen_state(self.occupancy_change, self.occupancy_id, new="off", duration = 30, immediate=True)


  def temp_change(self, entity, attribute, old, new, kwargs):
     self.temp_state = self.get_state(self.temperature_id)
     self.temp_uom = self.get_state(self.temperature_id, attribute="unit_of_measurement")
     self.humi_state = self.get_state(self.humidity_id)
     self.humi_uom = self.get_state(self.humidity_id, attribute="unit_of_measurement")
     self.occu_state = self.utils.binary_conversion(self.get_state(self.occupancy_id), reverse=self.binary_reverse)
     self.clim_state = self.get_state(self.climate_id)
     self.fans_state = self.get_state(self.climate_id, attribute="fan_mode")
     self.last_change = self.get_state(self.climate_id, attribute="last_changed")
     self.now = datetime.datetime.now()
     
     self.log("[INFO] Entity ID is {}".format(self.friendly_name(entity)))  
     self.log("[INFO] Temperature is {}".format(self.temp_state))
     self.log("[INFO] Humidity is {}".format(self.humi_state))
     self.log("[INFO] Occupancy is {}".format(self. occu_state))
     self.log("[INFO] Climate is {}".format(self.clim_state))
     self.log("[INFO] Fan speed is {}".format(self.fans_state))
     self.log("[INFO] Last changed is {}".format(self.last_change))
     

     temp = float(self.temp_state)
     temp_result = self.temperature_test(temp)    
     
     self.log("[TEMP_CHANGE] Temperature is {} range.".format(temp_result))
          
     try:
         chgOn_exist = self.check_timer(self.changeOn)
     except:
         chgOn_exist = False
     self.log("[TEMP_CHANGE] Exception error chgOn_exist")
     
     try:    
         chgOff_exist = self.check_timer(self.changeOff)
     except:    
         chgOff_exist = False
         self.log("[TEMP_CHANGE] Exception error chgOff_exist")
     
     try: 
         chgFan_exist = self.check_timer(self.changeFan)
     except:
         chgFan_exist = False
         self.log("[TEMP_CHANGE] Exception error chgFan_exist")
         
     if temp_result == "above" and self.climate_state("off") == True and chgOn_exist == False:  
         self.log("[TEMP_CHANGE] enter If statement ON")
         run_sec = self.last_changed_sec_req(required_sec=240)
         self.changeOn = self.run_in(self.turn_on_aircon, run_sec, occupancy_test="on", 
                                      climate_state="off")
         self.changeFan = self.run_in(self.change_fan_aircon, run_sec +5, fan_test="medium", 
                                       occupancy_test="on", climate_state="on", 
                                           fan_speed="medium")
     elif (temp_result == "below" or temp_result == "lowerbound") and chgOff_exist == False \
           and self.climate_state("on") == True:  
         self.log("[TEMP_CHANGE] enter If statement OFF")
         run_sec = self.last_changed_sec_req(required_sec=1381)
         self.changeOff = self.run_in(self.turn_off_aircon, run_sec, climate_state="on")
     elif temp_result == "within" and self.climate_state("on") == True and chgFan_exist == False:
         run_sec = 5
         self.log("[TEMP_CHANGE] enter If statement FAN")
         self.changeFan = self.run_in(self.change_fan_aircon, run_sec, climate_state="on", 
                                           fan_test="low", fan_speed="low")   
     else:
         self.log("[TEMP_CHANGE] No Conditions met")    
            
  def occupancy_change(self, entity, attribute, old, new, kwargs):
     try: 
         self.log("[OCCUPANCY_CHANGE] {} is {}.".format(self.friendly_name(entity), new))
         new = self.utils.binary_conversion(new, reverse=self.binary_reverse)
    
         self.cancel_timers()
    
         if new == 'on' : 
             run_sec = 1
             self.log("[OCCUPANCY_CHANGE] State is {} so run temp_change in {}s.".format(new, run_sec))
             self.changeTemp = self.run_in(self.temp_change, run_sec, entity = entity, 
                                           attribute = attribute, old_state = old, new_state = new)
         elif new == 'off' :
             run_sec = 300
             self.log("[OCCUPANCY_CHANGE] State is {} so run turn_off_aircon in {}s.".format(new, run_sec))
             self.changeOff = self.run_in(self.turn_off_aircon, run_sec, occupancy_test="off", climate_state="on")
     except:
         self.log("[OCCUPANCY_CHANGE] Key error entity: {} attribute: {} old: {} new: {} kwargs: {}.".format(entity, attribute, old, new, kwargs))
          
  def turn_on_aircon(self, kwargs):
     self.log("[TURN ON] Turn on {}.".format(self.friendly_name(self.climate_id)), level="WARNING")
     self.call_service("climate/turn_on", entity_id = self.climate_id)
     self.notify_slack(change = "turn on")          
     
  def change_fan_aircon(self, kwargs):
     self.log("[CHANGE FAN] Change fan {} to {}.".format(self.friendly_name(self.climate_id), kwargs['fan_speed']), level="WARNING")  
     self.call_service("climate/set_fan_mode", entity_id = self.climate_id, fan_mode = kwargs['fan_speed'])
     self.notify_slack(change = ("mode to " + kwargs['fan_speed']) )     
     
  def turn_off_aircon(self, kwargs):
     self.log("[TURN OFF] Turn off {}.".format(self.friendly_name(self.climate_id)), level="WARNING")   
     self.call_service("climate/turn_off", entity_id = self.climate_id)
     self.notify_slack(change = "turn off")     

  def notify_slack(self, change):     
     message = "Aircon {} - {}. Temp: {}{}. Humidity: {}{}.".format(change, self.friendly_name(self.climate_id), self.temp_state, self.temp_uom, self.humi_state, self.humi_uom)
     return self.utils.notify_slack(message)
    
  def temperature_test(self, ftemp):
     f = float(ftemp)
     res = 'ignore'
     if f >= 27.0 :
         res = 'above'
     elif 25.0 <= f < 26.5 :
         res = 'within'
     elif 24.5 <= f < 25.0 :
         res = 'below'  
     elif f < 24.5 :
         res = 'lowerbound'
     else:
         res = 'None'    
     return res
     
  def occupancy_test(self, state):
    actual_state=self.utils.binary_conversion(self.get_state(self.occupancy_id), reverse=self.binary_reverse)
    return self.utils.occupancy_test(self.occupancy_id, state, actual_state)

  def fan_test(self, state):
    if state != self.fans_state :
        self.log("[FAN_TEST] Actual state is {}, and required state is {} so return True.".format(self.fans_state, state))
        return True
    else :
        self.log("[FAN_TEST] Actual state is {}, and required state is {} so return False.".format(self.fans_state, state))
        return False
        
  def climate_state(self, state):
    return self.utils.climate_state(state, self.climate_id)

  def last_changed_sec_req(self, required_sec):
    return self.utils.last_changed_sec_req(required_sec, self.climate_id)

  def check_timer(self, handle):
    time, interval, kwargs = self.info_timer(handle)
    now = self.datetime()
    delta = time - now
    if delta.total_seconds() >= 0 :
        result = True
    else:
        result = False
    self.log("[CHECK_TIMER] {} exists. time is {}, interval is {} kwargs is {}. Delta is {} so return {}.".format(handle, time, interval, kwargs, delta, result))
    return result

  def cancel_timers(self):      
     try :
         self.cancel_timer(self.changeOn)
         self.log("[CANCEL TIMERS] self.change_on cancelled.")
     except : 
         self.log("[CANCEL TIMERS] can not cancel self.change_on.")
     try :
         self.cancel_timer(self.changeOff)
         self.log("[CANCEL TIMERS] self.change_off cancelled.")
     except: 
         self.log("[CANCEL TIMERS] can not cancel self.change_off.")
     try :
         self.cancel_timer(self.changeFan)
         self.log("[CANCEL TIMERS] self.change_fan cancelled.")
     except: 
         self.log("[CANCEL TIMERS] can not cancel self.change_fan.")

  def log(self,message,level="INFO"):
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