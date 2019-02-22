import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Climate Automation app
#
# Args:
#

class Media_control(hass.Hass):

  def initialize(self):
     self.utils = self.get_app("utilities")  
  
     self.AVR = self.args["avr_id"]
     self.TV = self.args["tv_id"]
     self.UNI = self.args["uni_id"]
     self.TVB_SWITCH = self.args["tvb_switch"]
     self.ATV_MEDIA_PLAYER = self.args["atv_media_player"]
     self.INPUT_SELECT_MEDIA = self.args["input_select_media"]
     self.RESET_FLAG = False

    
     self.register_constraint("media_state")
     self.register_constraint("source_state")

     
     self.LOGLEVEL=self.args["LOGLEVEL"]
     
     self.listen_state(self.media_select, self.UNI, attribute="source", media_state="playing")
     self.listen_state(self.reset_hdmi_trigger, self.UNI, new="off", duration=5)
     self.listen_state(self.media_select, self.UNI, old="off", new="playing", duration=10)

  def media_lookup(self, key):
     """
     Add bluetooth or music or spotify
     """

     info = {
                    "MyTVSuper" : ["Home Theatre", "CBL/SAT","avr"],
                    "YouTube" :  ["YouTube","TV Audio", "TV"],
                    "Apple TV" : ["Home Theatre", "Media Player","avr"],
                    "Live TV" : ["Live TV","TV Audio", "TV"],
                    "Plex" :  ["Plex","TV Audio", "TV"],
                    "Blue-ray" : ["Blue-ray PLAYER", "TV Audio","TV"],
                    "playing" : ["Live TV","TV Audio", "TV"]

            }
     try:
         tv_source  = info[key][0]
         avr_source = info[key][1]
         keysource_type = info[key][2]
     except:
         tv_source = "Live TV"
         avr_source = "TV Audio"
         keysource_type = "TV"
     return tv_source, avr_source, keysource_type

  def reset_hdmi_trigger(self, entity, attribute, old, new, kwargs):
     self.log("[RESET_HDMI_TRIGGER] entity: {}, attribute: {}, old: {}, new: {}, kwargs {}.".format(entity, attribute, old, new, kwargs))
     if self.utils.entity_state(self.ATV_MEDIA_PLAYER) != "off":
         self.log("[RESET_HDMI_TRIGGER] Entity state ATV is OK?: {}".format(self.utils.entity_state(self.ATV_MEDIA_PLAYER)))
         self.turn_off(self.ATV_MEDIA_PLAYER)           
         self.log("[RESET_HDMI_TRIGGER] Entity state ATV is OK?: {}".format(self.utils.entity_state(self.ATV_MEDIA_PLAYER)))
     

     
  def media_select(self, entity, attribute, old, new, kwargs):

     self.log("[MEDIA_SELECT] entity: {}, attribute: {}, old: {}, new: {}, kwargs {}.".format(entity, attribute, old, new, kwargs))     
     tv_source, avr_source, keysource_type = self.media_lookup(new)
     self.log("[MEDIA_SELECT] tv_source: {}, avr_source: {}, keysource_type: {}, new: {}.".format(tv_source, avr_source, keysource_type, new))
 
     if self.get_source(self.TV) != tv_source :
           self.select_source(new_entity=self.TV, source=tv_source)
           self.log("[MEDIA_SELECT] Set TV Source to: {}.".format(tv_source))
           
     
     if self.get_source(self.AVR) != avr_source :
           self.select_source(new_entity=self.AVR, source=avr_source) 
           self.log("[MEDIA_SELECT] Set AVR Source to: {}.".format(avr_source))
  
     if new == "MyTVSuper" :
        if self.utils.entity_state(self.TVB_SWITCH) == "off":
           self.turn_on_switch()
     else:
        if self.utils.entity_state(self.TVB_SWITCH) == "on":
           self.turn_off_switch()  
           
     if new == "Apple TV" and self.utils.entity_state(self.ATV_MEDIA_PLAYER) != "off":     
        self.turn_on(self.ATV_MEDIA_PLAYER)           
            
  def turn_on(self, new_entity):
     self.log("[TURN ON] Turn on {}.".format(self.friendly_name(new_entity)), level="WARNING")
     self.call_service("media_player/turn_on", entity_id = new_entity)
    
  def turn_off(self, new_entity):
     self.log("[TURN OFF] Turn off {}.".format(self.friendly_name(new_entity)), level="WARNING")
     self.call_service("media_player/turn_off", entity_id = new_entity)
     
  def select_source(self, new_entity, source):
     self.log("[SELECT_SOURCE] Select source {} for {}.".format(self.friendly_name(new_entity), source), level="WARNING")
     self.call_service("media_player/select_source", entity_id = new_entity, source=source)

  def turn_on_switch(self):
     self.log("[TURN ON] Turn on {}.".format(self.friendly_name(self.TVB_SWITCH)), level="WARNING")
     self.call_service("switch/turn_on", entity_id = self.TVB_SWITCH)
    
  def turn_off_switch(self):
     self.log("[TURN OFF] Turn off {}.".format(self.friendly_name(self.TVB_SWITCH)), level="WARNING")   
     self.call_service("switch/turn_off", entity_id = self.TVB_SWITCH)

  def get_source(self, entity_id):
     """
     Return Actual state of entity
     """
     try: 
        state = self.get_state(entity_id, attribute="source")
        self.log("[GET_SOURCE] Return source {} for {}.".format(state, entity_id))
        return state
     except:
        self.log("[GET_SOURCE] Exception error retrieving source for {}".format(entity_id), level="ERROR")
        return None    

  def notify_slack(self, change):
     message     = "{} - {}. Temp: {}{}. Humidity: {}{}.".format(self.friendly_name(self.dehum_id), change, self.temp_state, self.temp_uom, self.humi_state, self.humi_uom)   
     return self.utils.notify_slack(message)

  def media_state(self, state):
    result = self.utils.state_test(self.UNI, state)
    self.log("[MEDIA_STATE_CONSTRAINT] {}: required state is {} so result is: {}".format(self.UNI, state, result))
    return result
    
  def source_state(self, state):
    result = self.utils.state_test(self.INPUT_SELECT_MEDIA, state)
    if result is True:
       result = False
    else:
       result = True
    self.log("[SOURCE_STATE] {} return result of {}".format(self.INPUT_SELECT_MEDIA, result))
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