import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class Dehumidifier(hass.Hass):

  def initialize(self):
     self.utils = self.get_app("utilities")  
  
     self.temperature_id = self.args["temperature_id"]
     self.humidity_id = self.args["humidity_id"]
     self.climate_id = self.args["climate_id"]
     self.dehum_id = self.args["dehum_id"]
     self.UPPER = self.args["upper"]
     self.LOWER = self.args["lower"]
     
     self.LOGLEVEL=self.args["LOGLEVEL"]
     
     self.register_constraint("dehumidifier_state")
     self.register_constraint("climate_state")
     self.register_constraint("last_changed_clim")
     
     self.listen_state(self.humi_change, self.humidity_id)
     self.listen_state(self.humi_change, self.climate_id, duration = 10, climate_state="on")

  def humi_change(self, entity, attribute, old, new, kwargs):
     self.temp_state = self.get_state(self.temperature_id)
     self.temp_uom = self.get_state(self.temperature_id, attribute="unit_of_measurement")
     self.humi_state = self.get_state(self.humidity_id)
     self.humi_uom = self.get_state(self.humidity_id, attribute="unit_of_measurement")
     self.clim_state = self.get_state(self.climate_id)
     self.last_change_clim = self.get_state(self.climate_id, attribute="last_changed")
     self.dehum_state = self.get_state(self.dehum_id)
     self.last_change_dehum = self.get_state(self.dehum_id, attribute="last_changed")
     self.now = datetime.datetime.now()
     
     self.log("[INFO] Entity ID is {}".format(self.friendly_name(entity)))  
     self.log("[INFO] Temperature is {}".format(self.temp_state))
     self.log("[INFO] Humidity is {}".format(self.humi_state))
     self.log("[INFO] Climate is {}".format(self.clim_state))
     self.log("[INFO] Last changed is {}".format(self.last_change_clim))    
     self.log("[INFO] Dehumidifier is {}".format(self.dehum_state))
     self.log("[INFO] Last changed is {}".format(self.last_change_dehum))    

     humi = float(self.humi_state)
     humi_result = self.humidity_test(humi)    
     
     self.log("[HUMI_CHANGE] Humidity is {} range.".format(humi_result))
  
     try:
         chgOn_exist = self.check_timer(self.changeOn)
     except:
         chgOn_exist = False
         self.log("[HUMI_CHANGE] Exception error chgOn_exist")
     
     try:    
         chgOff_exist = self.check_timer(self.changeOff)
     except:    
         chgOff_exist = False
         self.log("[HUMI_CHANGE] Exception error chgOff_exist")
         
     if humi_result == "above" and float(self.temp_state) < 30.0 and chgOn_exist == False \
           and self.dehumidifier_state("off") == True :  
         self.log("[HUMI_CHANGE] enter If statement ON")
         run_sec = self.last_changed_sec_req(required_sec=240)
         self.changeOn = self.run_in(self.turn_on_switch, run_sec, dehumidifier_state="off", 
                                      climate_state="off", last_changed_clim="3600")
     elif (humi_result == "below" or self.climate_state("on") == True or float(self.temp_state) >= 31.0) \
           and chgOff_exist == False and self.dehumidifier_state("on") == True:  
         self.log("[HUMI_CHANGE] enter If statement OFF")
         run_sec = self.last_changed_sec_req(required_sec=240)
         self.changeOff = self.run_in(self.turn_off_switch, run_sec, dehumidifier_state="on")  
     else:
         self.log("[HUMI_CHANGE] No Conditions met")   
            
  def turn_on_switch(self, kwargs):
     self.log("[TURN ON] Turn on {}.".format(self.friendly_name(self.dehum_id)), level="WARNING")
     self.call_service("switch/turn_on", entity_id = self.dehum_id)
     self.notify_slack(change = "turn on")     
    
  def turn_off_switch(self, kwargs):
     self.log("[TURN OFF] Turn off {}.".format(self.friendly_name(self.dehum_id)), level="WARNING")   
     self.call_service("switch/turn_off", entity_id = self.dehum_id)
     self.notify_slack(change = "turn off")     

  def notify_slack(self, change):
     message     = "{} - {}. Temp: {}{}. Humidity: {}{}.".format(self.friendly_name(self.dehum_id), change, self.temp_state, self.temp_uom, self.humi_state, self.humi_uom)   
     return self.utils.notify_slack(message)
     
  def humidity_test(self, fhumi):
     f = float(fhumi)
     res = 'None'
     if f >= self.UPPER :
         res = 'above'
     elif self.LOWER <= f < self.UPPER :
         res = 'within'  
     elif f < self.LOWER :
         res = 'below' 
     return res

  def dehumidifier_state(self, state):
    return self.utils.state_test(self.dehum_id, state)

  def climate_state(self, state):
    return self.utils.climate_state(state, self.climate_id)

        
  def last_changed_clim(self, sec):
    return self.utils.last_changed(sec, self.climate_id)


  def last_changed_sec_req(self, required_sec):
      return self.utils.last_changed_sec_req(required_sec, self.dehum_id)


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