import appdaemon.plugins.hass.hassapi as hass
import datetime
import os.path
#
# Climate Automation app
#
# Args:
#

class Utils(hass.Hass):

    def initialize(self):
        """
        Add tests here are
        """   
              
        self.LOGLEVEL=self.args["LOGLEVEL"]
        self.PATH = self.args["path"]
        
        handle1 = self.run_in(self.entity_state_callback, 5, entity_id="input_boolean.alarm_silence")
        handle2 = self.run_in(self.entity_state_callback, 5, entity_id="error")


        result = self.check_timer_exist(handle1)
        self.log("[TEST1] {}, check_timer_exist for handle1".format(result))

        
        result = self.timer_exist(handle1)
        self.log("[TEST2] {}, timer_exist for handle1".format(result))

        result = self.timer_exist(handle2)
        self.log("[TEST3] {}, timer_exist for handle2".format(result))

#        result = self.notify_slack("test message")
#        self.log("[TEST4] {}, notify_slack".format(result))

        result = self.entity_state("blah")
        self.log("[TEST5] {}, for entity_state".format(result))

        result = self.entity_state("input_boolean.alarm_silence")
        self.log("[TEST6] {}, for entity_state".format(result))

        result = self.state_test("blah", "on")
        self.log("[TEST7] {}, for state_test".format(result))
  
        result = self.state_test("input_boolean.alarm_silence", "on")
        self.log("[TEST8] {}, for state_test".format(result))
        
        result = self.state_test("input_boolean.alarm_silence", "off")
        self.log("[TEST9] {}, for state_test".format(result))
        
        result = self.occupancy_test("blah", "on")
        self.log("[TEST10] {}, for occupancy_test".format(result))
  
        result = self.occupancy_test("binary_sensor.occupancy_mainbedroom", "on")
        self.log("[TEST11] {}, for occupancy_test".format(result))
        
        result = self.occupancy_test("binary_sensor.occupancy_mainbedroom", "off")
        self.log("[TEST12] {}, for occupancy_test".format(result))
        
        result = self.climate_state("on", "climate.at_room")
        self.log("[TEST13] {}, for climate_state".format(result))
        
        result = self.climate_state("off", "climate.at_room")
        self.log("[TEST14] {}, for climate_state".format(result))
        
        result = self.last_changed(300, "climate.at_room")
        self.log("[TEST15] {}, for last_changed".format(result))
  
        result = self.last_changed_sec("climate.at_room")
        self.log("[TEST16] Climate.At_room last_changed {}s".format(result))  
        
        result = self.last_changed_sec_req(300, "climate.at_room")
        self.log("[TEST17] {}, for last_changed sec required".format(result))
        
        result = self.last_changed_sec_req(3000, "climate.at_room")
        self.log("[TEST18] {}, for last_changed sec required".format(result))

        result = self.binary_conversion("on")
        self.log("[TEST19] {}, for binary_conversion".format(result))
        
#        message=""
#        target = "#error, #smoke"
#        color = "green"       
#        result =self.notify_slack(message, target=target, color=color)
#        result =self.notify_slack(message, entity_id="binary_sensor.multisensor1_sensor", target=target, color=color)
#        filename="/Volumes/Macintosh HD2/home/hac/images/2018_6_5_14_45_37_0_camera.living_room_camera.jpg"
#        self._notify_slack_image("test", filename)

    def timer_exist(self, handle):
        """
        Wrapper for check_timer_exist.
        Return True or False depending if the specified handler exists or not
        """
#    try: 
        result = self.check_timer_exist(handle)
        self.log("[TIMER_EXIST] For {}, result is {}".format(handle, result))
        return result
#    except:
#        self.log("[TIMER_EXIST] Exception error with handle {}".format(handle), level="ERROR")
#        return False
  
    def check_timer_exist(self, handle):
        """
        Return True or False depending if the specified handler exists in the future
        """
#    try: 
        time, interval, kwargs = self.info_timer(handle)
        now = self.datetime()
        delta = time - now
        if delta.total_seconds() >= 0 :
            result = True
        else:
            result = False
        self.log("[CHECK_TIMER_EXIST] For {}, time is {}, interval is {}, kwargs is {}, \
                 now is {}, delta is {} and result is {}".format(handle, time, interval, 
                 kwargs, now, delta, result))
                 
        return result
#    except: 
#        self.log("[CHECK_TIMER] Exception error with handle {}".format(handle), level="ERROR")
#        return False
       
    def list_to_dict(self, txt1, txt2):        
        """
        Return True or False depending if the specified handler exists in the future
        """
        try: 
            list1 = txt1.split(", ")
            list2 = txt2.split(", ")
            while len(list1) > len(list2):
                obj = list2[len(list2) - 1]
                list2.append(obj)
            d = dict(zip(list1, list2))
            self.log("[LIST_TO_DICT] Dictionary {} and Final tgt:color length {}:{}".format(d, len(list1), len(list2)))   
            return d  
        except:
            self.log("[LIST_TO_DICT] Exception error combining {} and {}".format(txt1, txt2), level="ERROR")
            return None 

    def notify_slack(self, message, entity_id=None, device_class=None, target=None, color=None):
        """
        Return True if notify/slack service executed successfully
        """
        try:
            dclass_list  = ['connectivity', 'door', 'window', 'opening', 'smoke']
            key_sensor_list  = ['binary_sensor.multisensor1_sensor', 'binary_sensor.main_door_sensor']
            key_sensor  = "binary_sensor.multisensor1_sensor"
            camera_id   = "camera.living_room_camera"
            aa_presence = self.state_test("binary_sensor.aa_presence", "on")
            tgt_color   = None
            
            if entity_id in key_sensor_list:
                key_sensor = entity_id
        
            if target is None:
                if color is None:
                    tgt_color = {'#info' : 'good'}
                    self.log("[NOTIFY_SLACK] Dictionary (1) {}".format(tgt_color))
    
                elif color is not None:
                    tgt_color = {'#info' : color}
                    self.log("[NOTIFY_SLACK] Dictionary (2) {}".format(tgt_color))
    
            elif target is not None:
                if color is None:
                    tgt_color = dict.fromkeys(target.split(", "), 'good')
                    self.log("[NOTIFY_SLACK] Dictionary (3) {}".format(tgt_color))
    
                elif color is not None:
                    tgt_color = self.list_to_dict(target, color)
                    self.log("[NOTIFY_SLACK] Dictionary (4) {}".format(tgt_color))
            
            if tgt_color is None :
                tgt_color = {'#info' : 'good'}
            if '#info' not in tgt_color :         # add info channel by default
                tgt_color['#info'] = 'good'
            if '#warn' not in tgt_color:         # add warn channel under certain conditions
                if device_class is not None :
                    try:
                        if device_class in dclass_list :
                            tgt_color['#warn'] = 'good'
                            self.log("[NOTIFY_SLACK] device_class {} matches so adding Warn to Dct {}".format(device_class, tgt_color))
                    except:
                        pass
                if aa_presence == False :
                    tgt_color['#warn'] = 'good'
                    self.log("[NOTIFY_SLACK] aa_presence = False so adding Warn to Dct {}".format(tgt_color))
    
                if entity_id == key_sensor:    
                    tgt_color['#warn'] = 'good'
                    self.log("[NOTIFY_SLACK] {} = {} so adding Warn to Dct {}".format(entity_id, key_sensor, tgt_color))
    
    
            self.log("[NOTIFY_SLACK] Final Dictionary {}".format(tgt_color))
            
            if entity_id == key_sensor:
                filename_notify, filename = self.camera_snapshot(camera_id)
                
            for key, value in tgt_color.items():
                if entity_id == key_sensor:
                    kwargs = {"filename" : filename, "filename_notify" : filename_notify, "snap" : True, "message" : message, "target" : key, "color" : value, "camera_count" : 1}
                    self.camera_notification(kwargs)
                else:
                    self.log("[NOTIFY_SLACK] Targets are : {} and Color are : {}".format(key, value))
                    self._notify_slack(message, key, value)
                    
            return True 
        except: 
            self.log("[NOTIFY_SLACK] Exception error. Function returns False", level="ERROR")
            return False 

    def _notify_slack(self, message, target=None, color=None):
        try:
            t           = self.get_state('sensor.time')
            msg         = ''
            title       = message or 'HA automation' 
            text        = ' @ ' + t    
            target      = target or '#info'
            color       = color or 'good'
            
            data = { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] }
            self.call_service("notify/slack", target = target, message = msg, data = data)  
    
            self.log("[_NOTIFY_SLACK] Message sent to {}: {}".format(target, message))
            return True
        except:
            self.log("[_NOTIFY_SLACK] Exception error. Service call failed", level="ERROR")
            return False 
    
    def _notify_slack_image(self, message, filename, target=None, color=None):
        try:
            t           = self.get_state('sensor.time')
            title       = message or 'HA automation' 
            text        = ' @ ' + t    
            target      = target or '#info'
            color       = color or 'good'
            
            data = { "file" : { "path" : filename } }
            
            self.log("[_NOTIFY_SLACK_IMAGE] Data is {}".format(data))
            self.log("[_NOTIFY_SLACK_IMAGE] target = {}, message = {}, title= {}, data = {}".format(target, title, text, data))
            self.call_service("notify/slack", target = target, message = title, title= text, data = data)  
            return True 
        except:
            self.log("[_NOTIFY_SLACK] Exception error. Service call failed", level="ERROR")
            return False 

    def camera_snapshot(self, entity_id):
        now = self.datetime()
        timestamp = "{}_{}_{}_{}_{}_{}_{}".format(
                      now.year, now.month, now.day, now.hour,
                      now.minute, now.second, now.microsecond)
        filename = "{}/{}_{}.jpg".format(self.PATH, timestamp, entity_id) 
        filename_docker = "/images/{}_{}.jpg".format(timestamp, entity_id)     
        self.call_service("camera/snapshot", entity_id=entity_id, filename=filename)
        return filename, filename_docker

    def camera_notification(self, kwargs):
        self.log("[CAMERA_NOTIFICATION] kwargs: {}".format(kwargs))
        camera_count = kwargs['camera_count']

        self.log("[CAMERA_NOTIFICATION] camera_count: {}".format(camera_count))
        self.log("[CAMERA_NOTIFICATION] snap: {}".format(kwargs['snap']))
        
        result = os.path.isfile(kwargs['filename'])
        self.log("[CAMERA_NOTIFICATION] OS.PATH result is {}".format(result))
     
        if result is True:
            self.log("[CAMERA_NOTIFICATION] FOUND Filepath: {}".format(kwargs['filename']))
            self.log("[CAMERA_NOTIFICATION] USE Filepath: {}".format(kwargs['filename_notify']))

            result = self._notify_slack_image(kwargs['message'], kwargs['filename_notify'], kwargs['target'], kwargs['color'])
            self.log("[CAMERA_NOTIFICATION] Notify_slack_image: {}".format(result))

        else:
            camera_count += 1
            self.log("[CAMERA_NOTIFICATION] camera_count: {}".format(camera_count))
              
            if camera_count <= 10:
                self.run_in(self.camera_loop, 1, camera_count=camera_count, filename=kwargs['filename'], 
                        filename_notify=kwargs['filename_notify'], snap=False, 
                        message=kwargs['message'], target=kwargs['target'], color=kwargs['color'])
            else:
                pass
        
    def camera_loop(self, kwargs):
        self.log("[CAMERA_LOOP] kwargs: {}".format(kwargs))
        
        self.run_in(self.camera_notification, 1, camera_count=kwargs['camera_count'], filename=kwargs['filename'], 
                    filename_notify=kwargs['filename_notify'], snap=kwargs['snap'], 
                    message=kwargs['message'], target=kwargs['target'], color=kwargs['color'])
    
    def occupancy_test(self, entity_id, required_state, actual_state=None):
        """
        Wrapper for state_test
        Return occupancy as true or false depending of required state = actual state
        """
        try: 
            if actual_state is None :
                actual_state = self.entity_state(entity_id)
            result = self.state_test(entity_id, required_state, actual_state)
            self.log("[OCCUPANCY_TEST] For {}, result is {}".format(entity_id, result))
            return result
        except:
            self.log("[OCCUPANCY_TEST] Exception error retrieving state for {}".format(entity_id), level="ERROR")
            return False 

    def state_test(self, entity_id, required_state, actual_state=None):
        """
        Return True or False depending if actual state = required state
        Calls entity_state to get current state
        """
        try:   
            if actual_state is None :
                actual_state = self.entity_state(entity_id)         
            if required_state == actual_state:
                result = True
            else:
                result = False
            self.log("[STATE_TEST] For {}, actual state is {}, required state is {} and result is {}".format(
                     entity_id, actual_state, required_state, result))
            return result
        except:
            self.log("[STATE_TEST] Exception error retrieving state for {}".format(entity_id), level="ERROR")
            return False 

    def entity_state_callback(self, kwargs):
        """
        Return Actual state of entity
        """
        try: 
            entity_id = kwargs['entity_id']
            state = self.entity_state(entity_id)
            self.log("[ENTITY_STATE_CB] Return {} for {}.".format(state, entity_id))
        except:
            self.log("[ENTITY_STATE_CB] Exception error retrieving state for {}".format(entity_id), level="ERROR")
            return None 

    def entity_state(self, entity_id):
        """
        Return Actual state of entity
        """
        try: 
            state = self.get_state(entity_id)
            self.log("[ENTITY_STATE] Return {} for {}.".format(state, entity_id))
            return state
        except:
            self.log("[ENTITY_STATE] Exception error retrieving state for {}".format(entity_id), level="ERROR")
            return None           
        
    def climate_state(self, required_state, entity_id):
        """
        Return True or False depending if actual state = required state
        Calls entity_state to get current state
        """
#    try:   
        clim_state = self.entity_state(entity_id)  
            
        if (required_state == "on" and clim_state != "off" and clim_state != "unavailable") \
            or required_state == clim_state :
            result = True
        else:
            result = False
        self.log("[CLIMATE_STATE] For {}, actual state is {}, required state is {} and result is {}".format(
                 entity_id, clim_state, required_state, result))
        return result
#    except:
#        self.log("[CLIMATE_STATE] Exception error retrieving state for {}".format(entity_id), level="ERROR")
#        return False 
        
    def last_changed(self, sec, entity_id):
        """
        Return True if the entity's last changed is after the threshold in seconds
        """
        try:
            sec_int = int(sec)
            delta_int = self.last_changed_sec(entity_id)
            if delta_int > sec_int :
                result = True
            else :
                result = False
            self.log("[LAST_CHANGED] For {}, sec_int is {}, delta_int is {} and result is {}".format(
                     entity_id, sec_int, delta_int, result))
            return result
        except:
            self.log("[LAST_CHANGED] Exception error last change test for {}".format(entity_id), level="ERROR")
            return False 
            
    def last_changed_sec(self, entity_id):
        """
        Return seconds since entity's last changed
        """
        try:
            now = self.datetime()
            last_change = self.convert_utc(self.get_state(entity_id, attribute="last_changed"))

            result = int( now.timestamp() - last_change.timestamp())

            self.log("[LAST_CHANGED_SEC] For {}, last_change is {}, delta_int is {}".format(
                     entity_id, last_change, result))
            return result    
        except:
            self.log("[LAST_CHANGED_SEC] Exception error last change sec for {}".format(entity_id), level="ERROR")
            return False 
            
    def last_changed_sec_req(self, required_sec, entity_id):
        """
        Return seconds as int for seconds needed to run by comparing 
        last changed status of respective variable
        """
        try: 
            req_sec_int = int(required_sec)
            delta_int = self.last_changed_sec(entity_id)

            if delta_int >= req_sec_int :
                result = 5
            else :
                result = int(req_sec_int - delta_int)        
            return result
            self.log("[LAST_CHANGED_SEC_REQ] For {}, req_sec_int is {}, delta_int is {} and result is {}".format(
                     entity_id, sec_int, delta_int, result))
        except:
            self.log("[LAST_CHANGED_SEC_REQ] Exception error calculating last change requirements for {}".format(entity_id), level="ERROR")
            return 0
            
    def binary_conversion(self, state, reverse=True):
        """
        Reverses the state of a binary sensor if reverse= True
        """
        try:
            if reverse == True:
                if state == "off" :
                    result = "on"
                else :
                    result = "off"
            else:
                result = state
            self.log("[BINARY_CONVERSION] Reverse is {}, original state is {} and result is {}".format(
                     reverse, state, result))
            return result
        except:
            self.log("[BINARY_CONVERSION] Exception error for binary conversion {}".format(state), level="ERROR")
            return False 
                
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
