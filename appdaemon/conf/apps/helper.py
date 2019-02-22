import appdaemon.plugins.hass.hassapi as hass
import datetime
#
# Helper module to support the smooth running of HA
#
# Args:
#

class Log_control(hass.Hass):

  def initialize(self):
     self.utils = self.get_app("utilities")  
     self.FILESENSOR = self.args["filesensor"]
     self.SIZE_LIMIT = self.args["size_limit"]
     self.register_constraint("file_big")
     
     self.LOGLEVEL=self.args["LOGLEVEL"]
     
     self.listen_state(self.clean_up, self.FILESENSOR, file_big=1)
     
  def clean_up(self, entity, attribute, old, new, kwargs):

     self.log("[CLEAN_UP] entity: {}, attribute: {}, old: {}, new: {}, kwargs {}.".format(entity, attribute, old, new, kwargs))     
     
     self.empty_log()
     self.run_in(self.notify_slack, 32)
            
  def empty_log(self):
     self.log("[EMPTY_LOG] Empty Log.", level="WARNING")
     self.call_service("script/empty_log")


  def get_size(self, entity_id):
     """
     Return Actual state of entity
     """
     try: 
        state = self.get_state(entity_id)
        self.log("[GET_SIZE] Return size {} for {}.".format(state, entity_id))
        return state
     except:
        self.log("[GET_SIZE] Exception error retrieving size for {}".format(entity_id), level="ERROR")
        return 0    
    
  def file_big(self, value):
    size = float(self.get_size(self.FILESENSOR))
    if size > self.SIZE_LIMIT :
        result = True
    else:
       result = False
    self.log("[FILE_BIG] {} return result of {}".format(self.FILESENSOR, result))
    return result

  def notify_slack(self, kwargs):
     size = self.get_size(self.FILESENSOR)
     message     = "{} has file size of {} after clean up.".format(self.friendly_name(self.FILESENSOR), size)   
     return self.utils.notify_slack(message)

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