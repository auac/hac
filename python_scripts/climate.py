# Get time and states
now                 = datetime.datetime.now()
t                   = hass.states.get('sensor.time').state
timestamp           = "{}_{}_{}_{}_{}_{}_{}".format(
                      now.year, now.month, now.day, now.hour,
                      now.minute, now.second, now.microsecond)
count1				= 0
count2				= 0
debug				= 'on'
debug2				= 'off'
debuginfo			= '[CLIMATE.PY]\n'

state_aa            = hass.states.get('input_boolean.presence_a').state
state_pt			= hass.states.get('input_boolean.presence_p').state
state_occupancy_all	= hass.states.get('binary_sensor.occupancy_all').state
AL_ROOM             = 'binary_sensor.door_window_sensor_158d000105e2a2'
AT_ROOM             = 'binary_sensor.door_window_sensor_158d000105d011'

# Define notification variables
target      = '#info'
msg         = ''
color       = 'good'
title       = 'HA automation' 
text        = ' @ ' + t


# define the entity mappings
Entity = ['climate.master_bedroom', 'binary_sensor.occupancy_mainbedroom', 'sensor.multisensor2_temperature', 'climate.at_room', AT_ROOM, 'sensor.at_room_temperature']
climateEntity = ['climate.master_bedroom' , 'climate.at_room' ]
tempEntity = ['sensor.multisensor2_temperature' , 'sensor.at_room_temperature' ]
humidityEntity = ['sensor.multisensor2_relative_humidity' , 'sensor.at_room_relative_humidity' ]
occupancyEntity = ['binary_sensor.occupancy_mainbedroom' , AT_ROOM ]

#def func2(msg, func1):
#    return 'result of func2("' + func1(msg) + '")'

#def func1(msg):
#    return 'result of func1("' + msg + '")'

#if debug == 'on' : debuginfo = debuginfo +  func1('test') )
#if debug == 'on' : debuginfo = debuginfo +  func2('test', func1) )


def occupancy_test(state_occupancy):
    if state_occupancy == 'on' :
        return 1
    else :
        return 0
   
def aa_pt_test(state_aa, state_pt):
    if state_aa == 'on' or state_pt == 'on' :
        return 1
    else :
        return 0
     

def presence_test(climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test):
    if climate_id == 'climate.master_bedroom' :
        res = aa_pt_test(state_aa, state_pt)
    else :
        res = occupancy_all_test(state_occupancy_all)
    return res
    
def occupancy_all_test(state_occupancy_all):
    if state_occupancy_all == 'on' :
        return 1
    else :
        return 0
    
def temperature_test(ftemp):
    f = float(ftemp)
    res = 'ignore'
    if f >= 27.0 :
        res = 'above'
    if 25.0 <= f < 26.5 :
        res = 'within'
    if 24.5 <= f < 25.0 :
        res = 'below'  
    if f < 24.5 :
        res = 'lowerbound' 
    return res

        
def last_changed(fnow, fdt, fsec):
    sec_int = int(fsec)
    delta_int = int( fnow.timestamp() - fdt.timestamp() )
    if delta_int > sec_int :
        return 1
    else :
        return 0
  
def conditions_on_test(ftemp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy):
    try: 
        p = presence_test(climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test)
        o = occupancy_test(state_occupancy)
        t = temperature_test(ftemp)
        l = last_changed(now, dt, fsec = 180)
    except:
        return 0
    else:
        if p == 1 and o == 1 and t == 'above' and l == 1 :
            return 1
        else :
            return 0
      
def conditions_fan_test(ftemp, temperature_test):
    try:
        t = temperature_test(ftemp)
    except:
        return 0
    else:
        if t == 'above' :
            return 'medium'
        elif t == 'within' :
            return 'low'
        else :
            return 0
          
def conditions_off_test(ftemp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy):
    try:
        o = occupancy_test(state_occupancy)
        t = temperature_test(ftemp)
        l = last_changed(now, dt, fsec = 1320)
    except:
        return 0
    else: 
        if ( o == 0 ) or ( t == 'below' and l == 1 ) or t == 'lowerbound' :
            return 1
        else :
            return 0

# Get script variables

trigger_entity	    = data.get('trigger_entity') or 'NO_ENTITY'
trigger_platform    = data.get('trigger_platform')
trigger_from_state  = data.get('trigger_from_state')
trigger_to_state    = data.get('trigger_to_state')

if debug == 'on' : debuginfo = debuginfo + 'Trigger entity: ' + trigger_entity + '.\n'
if debug == 'on' : debuginfo = debuginfo + 'Trigger platform: ' + trigger_platform + '.\n'
if debug == 'on' : debuginfo = debuginfo + 'Trigger from state: ' + trigger_from_state + '.\n'
if debug == 'on' : debuginfo = debuginfo + 'Trigger to state: ' + trigger_to_state + '.\n'

if trigger_entity == 'sensor.date__time' or \
  trigger_entity == 'input_boolean.presence_a' or \
  trigger_entity == 'input_boolean.presence_p' :
    trigger_entity = 'NO_ENTITY'

# where specific trigger entity identified

if trigger_entity != 'NO_ENTITY' :
  
  if debug == 'on' : debuginfo = debuginfo + 'if (1) condition. Trigger_entity == {}.\n'.format(trigger_entity)
  
  for e in Entity :

      if e == trigger_entity :
          break
          
      if count1 == 2 : 
          count1 = 0
          count2 = count2 + 1
      else:
          count1 = count1 + 1
  
  if debug2 == 'on' : debuginfo = debuginfo + 'Use count 2: {}.\n'.format(count2)
  

  climate_id = climateEntity[count2]
  temp_id = tempEntity[count2]
  humidity_id = humidityEntity[count2]
  occupancy_id = occupancyEntity[count2]

  

# get temp and humidity and entity state now that we know the right entity
  state_climate		= hass.states.get(climate_id).state
  fn				= hass.states.get(climate_id).attributes.get('friendly_name')
  fan_mode			= hass.states.get(climate_id).attributes.get('fan_mode')
  state_temp		= hass.states.get(temp_id).state
  tuom 				= hass.states.get(temp_id).attributes.get('unit_of_measurement')
  state_humidity	= hass.states.get(humidity_id).state
  huom 				= hass.states.get(humidity_id).attributes.get('unit_of_measurement')
  state_occupancy	= hass.states.get(occupancy_id).state
  dt 				= hass.states.get(climate_id).last_changed

# reverse the occupancy binary status for AT/AL room as we are using binar doors

  if occupancy_id == AL_ROOM or occupancy_id == AT_ROOM :
    if state_occupancy == 'off' :
      state_occupancy = 'on'
    else: 
      state_occupancy = 'off'
    
# Debug section:

  if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Climate: {}.\n'.format(climate_id, state_climate)
  if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Temperature: {}.\n'.format(temp_id, state_temp)
  if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Humidity: {}.\n'.format(humidity_id, state_humidity)
  if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Occupancy: {}.\n'.format(occupancy_id, state_occupancy)

  res = occupancy_test(state_occupancy)
  if debug2 == 'on' : debuginfo = debuginfo + 'occupancy_test:  return: {}.\n'.format(res)
  
  res = aa_pt_test(state_aa, state_pt)
  if debug2 == 'on' : debuginfo = debuginfo + 'aa_pt_test:  return: {}.\n'.format(res)
  
  res = presence_test(climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test)
  if debug2 == 'on' : debuginfo = debuginfo + 'presence_test:  return: {}.\n'.format(res)
  
  res = occupancy_all_test(state_occupancy_all)
  if debug2 == 'on' : debuginfo = debuginfo + 'occupancy_all_test:  return: {}.\n'.format(res)
  
  res = temperature_test(state_temp)
  if debug2 == 'on' : debuginfo = debuginfo + 'temperature_test:  return: {}.\n'.format(res)
  
  res = last_changed(now, dt, fsec = 180)
  if debug2 == 'on' : debuginfo = debuginfo + 'last_changed_180:  return: {}.\n'.format(res)

  res = last_changed(now, dt, fsec = 1320)
  if debug2 == 'on' : debuginfo = debuginfo + 'last_changed_1320:  return: {}.\n'.format(res)

# run the conditions testing:
  
  conditions_on = conditions_on_test(state_temp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy)
  conditions_fan = conditions_fan_test(state_temp, temperature_test)
  conditions_off = conditions_off_test(state_temp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy)
  
  if debug2 == 'on' : debuginfo = debuginfo + ' conditions_on_test: return: {}.\n conditions_fan_test: return: {}.\n conditions_off_test: return: {}.\n'.format(conditions_on, conditions_fan, conditions_off)


# take action based on test results  

  if conditions_on == 1 and state_climate == 'off' :
      data = { "entity_id" : climate_id }
      hass.services.call('climate', 'turn_on', data)
      title = 'Aircon turn on - {}. Temp: {}{}. Humidity: {}{}.'.format(fn, state_temp, tuom, state_humidity, huom)
      data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
      hass.services.call('notify', 'slack', data)
      if debug == 'on' : debuginfo = debuginfo + 'conditions_on met.\n'
      
  elif (conditions_fan == 'medium' or conditions_fan == 'low') and conditions_off == 0 and state_climate != 'off' and state_climate != 'unavailable' and fan_mode != conditions_fan :
      fan_mode = conditions_fan
      data = { "entity_id" : climate_id , "fan_mode" : fan_mode }
      hass.services.call('climate', 'set_fan_mode', data)
      title = 'Aircon turn {} - {}. Temp: {}{}. Humidity: {}{}.'.format(fan_mode, fn, state_temp, tuom, state_humidity, huom)
      data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
      hass.services.call('notify', 'slack', data)
      if debug == 'on' : debuginfo = debuginfo + 'conditions_fan met.\n'
  
  elif conditions_off == 1 and state_climate != 'off' and state_climate != 'unavailable' :
      data = { "entity_id" : climate_id }
      hass.services.call('climate', 'turn_off', data)
      title = 'Aircon turn off - {}. Temp: {}{}. Humidity: {}{}.'.format(fn, state_temp, tuom, state_humidity, huom)
      data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
      hass.services.call('notify', 'slack', data)
      if debug == 'on' : debuginfo = debuginfo + 'conditions_off met.\n'

  else:
      if debug == 'on' : debuginfo = debuginfo + 'conditions on not met: conditions_on: {}, state_climate: {}.\n'.format(conditions_on, state_climate)
      if debug == 'on' : debuginfo = debuginfo + 'conditions fan not met: conditions_fan: {}, conditions_off: {}, state_climate: {}, fan_mode: {}.\n'.format(conditions_fan, conditions_off, state_climate, fan_mode)
      if debug == 'on' : debuginfo = debuginfo + 'conditions off not met: conditions_off: {}, state_climate: {}.\n'.format(conditions_off, state_climate)
      if debug == 'on' : debuginfo = debuginfo + 'no conditions met.'
      
# if trigger entity not identifed then loop through and check all aircon units
  
else: 
  if debug == 'on' : debuginfo = debuginfo + 'Else (2) condition. Trigger_entity == {}.\n'.format(trigger_entity)
  
  climateEntity = [ 'climate.master_bedroom', 'climate.at_room' ]
  tempEntity = [ 'sensor.multisensor2_temperature', 'sensor.at_room_temperature' ]
  humidityEntity = [ 'sensor.multisensor2_relative_humidity', 'sensor.at_room_relative_humidity' ]
  occupancyEntity = [ 'binary_sensor.occupancy_mainbedroom', AT_ROOM ]

  for c in climateEntity :
      
      climate_id = climateEntity[count1]
      temp_id = tempEntity[count1]
      humidity_id = humidityEntity[count1]
      occupancy_id = occupancyEntity[count1]
      
      count1 = count1 + 1
      
      # get temp and humidity and entity state now that we know the right entity
      state_climate		= hass.states.get(climate_id).state
      fn				= hass.states.get(climate_id).attributes.get('friendly_name')
      fan_mode			= hass.states.get(climate_id).attributes.get('fan_mode')
      state_temp		= hass.states.get(temp_id).state
      tuom 				= hass.states.get(temp_id).attributes.get('unit_of_measurement')
      state_humidity	= hass.states.get(humidity_id).state
      huom 				= hass.states.get(humidity_id).attributes.get('unit_of_measurement')
      state_occupancy	= hass.states.get(occupancy_id).state
      dt 				= hass.states.get(climate_id).last_changed
     
      if occupancy_id == AL_ROOM or occupancy_id == AT_ROOM :
        if state_occupancy == 'off' :
          state_occupancy = 'on'
        else: 
          state_occupancy = 'off'
          
      # Debug section:

      if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Climate: {}.\n'.format(climate_id, state_climate)
      if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Temperature: {}.\n'.format(temp_id, state_temp)
      if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Humidity: {}.\n'.format(humidity_id, state_humidity)
      if debug == 'on' : debuginfo = debuginfo + 'Entity_ID: {}. Occupancy: {}.\n'.format(occupancy_id, state_occupancy)
  
      res = occupancy_test(state_occupancy)
      if debug2 == 'on' : debuginfo = debuginfo + 'occupancy_test:  return: {}.\n'.format(res)
  
      res = aa_pt_test(state_aa, state_pt)
      if debug2 == 'on' : debuginfo = debuginfo + 'aa_pt_test:  return: {}.\n'.format(res)
  
      res = presence_test(climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test)
      if debug2 == 'on' : debuginfo = debuginfo + 'presence_test:  return: {}.\n'.format(res)
  
      res = occupancy_all_test(state_occupancy_all)
      if debug2 == 'on' : debuginfo = debuginfo + 'occupancy_all_test:  return: {}.\n'.format(res)
  
      res = temperature_test(state_temp)
      if debug2 == 'on' : debuginfo = debuginfo + 'temperature_test:  return: {}.\n'.format(res)
  
      res = last_changed(now, dt, fsec = 180)
      if debug2 == 'on' : debuginfo = debuginfo + 'last_changed_180:  return: {}.\n'.format(res)

      res = last_changed(now, dt, fsec = 1320) 
      if debug2 == 'on' : debuginfo = debuginfo + 'last_changed_1320:  return: {}.\n'.format(res)
      
      conditions_on = conditions_on_test(state_temp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy)
      conditions_fan = conditions_fan_test(state_temp, temperature_test)
      conditions_off = conditions_off_test(state_temp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy)
  
      if debug2 == 'on' : debuginfo = debuginfo + ' conditions_on_test: return: {}.\n conditions_fan_test: return: {}.\n conditions_off_test: return: {}.\n'.format(conditions_on, conditions_fan, conditions_off)

  
      if conditions_on == 1 and state_climate == 'off' :
          data = { "entity_id" : climate_id }
          hass.services.call('climate', 'turn_on', data)
          title = 'Aircon turn on - {}. Temp: {}{}. Humidity: {}{}.'.format(fn, state_temp, tuom, state_humidity, huom)
          data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
          hass.services.call('notify', 'slack', data)
          if debug == 'on' : debuginfo = debuginfo + 'conditions_on met.\n'

      elif (conditions_fan == 'medium' or conditions_fan == 'low') and conditions_off == 0 and state_climate != 'off' and state_climate != 'unavailable' and fan_mode != conditions_fan :
          fan_mode = conditions_fan
          data = { "entity_id" : climate_id , "fan_mode" : fan_mode }
          hass.services.call('climate', 'set_fan_mode', data)
          title = 'Aircon turn {} - {}. Temp: {}{}. Humidity: {}{}.'.format(fan_mode, fn, state_temp, tuom, state_humidity, huom)
          data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
          hass.services.call('notify', 'slack', data)
          if debug == 'on' : debuginfo = debuginfo + 'conditions_fan met.\n'

      elif conditions_off == 1 and state_climate != 'off' and state_climate != 'unavailable' :
          data = { "entity_id" : climate_id }
          hass.services.call('climate', 'turn_off', data)
          title = 'Aircon turn off - {}. Temp: {}{}. Humidity: {}{}.'.format(fn, state_temp, tuom, state_humidity, huom)
          data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
          hass.services.call('notify', 'slack', data)
          if debug == 'on' : debuginfo = debuginfo + 'conditions_off met.\n'

      else:
          if debug == 'on' : debuginfo = debuginfo + 'conditions on not met: conditions_on: {}, state_climate: {}.\n'.format(conditions_on, state_climate)
          if debug == 'on' : debuginfo = debuginfo + 'conditions fan not met: conditions_fan: {}, conditions_off: {}, state_climate: {}, fan_mode: {}.\n'.format(conditions_fan, conditions_off, state_climate, fan_mode)
          if debug == 'on' : debuginfo = debuginfo + 'conditions off not met: conditions_off: {}, state_climate: {}.\n'.format(conditions_off, state_climate)
          if debug == 'on' : debuginfo = debuginfo + 'no conditions met'

          
# send log for debug info  
logger.error(debuginfo)
          
          
    
    

