import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class Test(hass.Hass):

  def initialize(self):
     self.inputboolean = "input_boolean.alarm_silence"
     self.register_constraint("check_timer")   


     self.listen_state(self.temp_change, self.inputboolean, duration = 10)

  def temp_change(self, entity, attribute, old, new, kwargs):
 
     self.now = datetime.datetime.now()
     

#     if (temp_result != "below" or temp_result != "lowerbound") and occu_test == True :
#         self.cancel_timers(kwargs)      
     try:
         result = self.check_timer(self.runningCheck)
         self.log("[TEMP_CHANGE] Result of check 1 timer is {}.".format(result))
     except:
         self.log("[TEMP_CHANGE] Error")

     self.runningCheck = self.run_in(self.occupancy_test, 1000, state="on", occu_state=new)
     result = self.check_timer(self.runningCheck)
     self.log("[TEMP_CHANGE] Result of check 2 timer is {}.".format(result))
     
     
  def notify_slack(self, change):
     t           = self.get_state('sensor.time')
     target      = '#info'
     msg         = ''
     color       = 'good' 
     title       = 'HA automation' 
     text        = ' @ ' + t
     title = "Aircon {} - {}. Temp: {}{}. Humidity: {}{}.".format(change, self.friendly_name(self.climate_id), self.temp_state, self.temp_uom, self.humi_state, self.humi_uom)
     data = { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] }
     self.call_service("notify/slack", target = target, message = msg, data = data)    
     
     
  
     
  def occupancy_test(self, kwargs):
    if kwargs['state'] == kwargs['occu_state'] :
        self.log("[OCCUPANCY_TEST] Actual state is {}, and required state is {} so return True.".format(kwargs['occu_state'], kwargs['state']))  
        return True
    else :
        self.log("[OCCUPANCY_TEST] Actual state is {}, and required state is {} so return False.".format(kwargs['occu_state'], kwargs['state']))  
        return False
        
  def last_changed(self, sec):
    sec_int = int(sec)
    self.now = datetime.datetime.now()
    self.last_change = self.get_state(self.climate_id, attribute="last_changed")
    var1 = self.last_change[0:(len(self.last_change) - 3)] 
    var2 = self.last_change[(len(self.last_change) - 2):len(self.last_change)]
    last_change_str = var1 + var2
    last_change_time = datetime.datetime.strptime(last_change_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    delta_int = int( self.now.timestamp() - last_change_time.timestamp() )
    self.log("[LAST_CHANGED] Climate changed {} seconds ago vs test bound of {} seconds.".format(delta_int, sec_int))   

    if delta_int > sec_int :
        return True
    else :
        return False

  def last_changed_sec_req(self, required_sec):
    req_sec_int = int(required_sec)
    
    self.now = datetime.datetime.now()
    self.last_change = self.get_state(self.climate_id, attribute="last_changed")

    var1 = self.last_change[0:(len(self.last_change) - 3)] 
    var2 = self.last_change[(len(self.last_change) - 2):len(self.last_change)]
    last_change_str = var1 + var2
    last_change_time = datetime.datetime.strptime(last_change_str, "%Y-%m-%dT%H:%M:%S.%f%z")
    delta_int = int( self.now.timestamp() - last_change_time.timestamp())
    
    if delta_int > req_sec_int :
        result = 5
    else :
        result = int(req_sec_int - delta_int)

    self.log("[LAST_CHANGED SEC REQ] Last changed {}s ago vs required of {}s, so set run_in for {}s.".format(
                                      delta_int, req_sec_int, result))           
    return result

  def check_timer(self, handle):
        time, interval, kwargs = self.info_timer(handle)
        now = datetime.datetime.now()
        delta_int = int(time.timestamp() - now.timestamp())
        if delta_int > 0 :
            self.log("[CHECK_TIMER] {} exists. time is {}, interval is {} kwargs is {}. Delta is {} so return False.".format(handle, time, interval, kwargs, delta_int))
            result = False
        else:
            self.log("[CHECK_TIMER] {} exists. time is {}, interval is {} kwargs is {}. Delta is {} so return True.".format(handle, time, interval, kwargs, delta_int))
            result = True
        return result

  def cancel_timers(self, kwargs):      
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
