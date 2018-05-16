# Get time and states
now                 = datetime.datetime.now()
t                   = hass.states.get('sensor.time').state
timestamp           = "{}_{}_{}_{}_{}_{}_{}".format(
                      now.year, now.month, now.day, now.hour,
                      now.minute, now.second, now.microsecond)
count               = -1
debug				= 'off'
debug2				= 'on'

state_aa            = hass.states.get('input_boolean.presence_a').state
state_pt			= hass.states.get('input_boolean.presence_b').state
state_occupancy_all	= hass.states.get('binary_sensor.occupancy_all').state
state_mb_room 		= hass.states.get('binary_sensor.occupancy_mainbedroom').state
state_lv_room 		= hass.states.get('binary_sensor.living_room_motion').state
state_al_room 		= hass.states.get('binary_sensor.al_door').state
state_at_room 		= hass.states.get('binary_sensor.at_door').state


# Define notification variables
target      = '#info'
msg         = ''
color       = 'good'
title       = 'HA automation' 
text        = ' @ ' + t


# define the entity mappings
Entity = ['binary_sensor.occupancy_mainbedroom', 'sensor.multisensor2_temperature']
#Entity = ['binary_sensor.occupancy_mainbedroom', 'sensor.multisensor2_temperature']
climateEntity = ['climate.master_bedroom', 'climate.master_bedroom']
tempEntity = ['sensor.multisensor2_temperature', 'sensor.multisensor2_temperature']
humidityEntity = ['sensor.multisensor2_relative_humidity', 'sensor.multisensor2_relative_humidity']
occupancyEntity = ['binary_sensor.occupancy_mainbedroom', 'binary_sensor.occupancy_mainbedroom']

def func2(msg, func1):
    return 'result of func2("' + func1(msg) + '")'

def func1(msg):
    return 'result of func1("' + msg + '")'

if debug == 'on' : logger.error( func1('test') )
if debug == 'on' : logger.error( func2('test', func1) )


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
  if f < 25.0 :
      res = 'below'   
  return res
      
def last_changed(fnow, fdt, fsec):
  sec_int = int(fsec)
  delta_int = int( fnow.timestamp() - fdt.timestamp() )
  if delta_int > sec_int :
      return 1
  else :
      return 0
  
def conditions_on_test(ftemp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy):
  p = presence_test(climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test)
  o = occupancy_test(state_occupancy)
  t = temperature_test(ftemp)
  l = last_changed(now, dt, fsec = 900)
  if p == 1 and o == 1 and t == 'above' and l == 1 :
      return 1
  else :
      return 0
      
def conditions_low_test(ftemp, temperature_test):
  t = temperature_test(ftemp)
  if t == 'within' :
      return 1
  else :
      return 0
      
def conditions_off_test(ftemp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy):
  o = occupancy_test(state_occupancy)
  t = temperature_test(ftemp)
  l = last_changed(now, dt, fsec = 1320)
  if ( o == 0 ) or ( t == 'below' and l == 1 ):
      return 1
  else :
      return 0
      
def turn_on_aircon(climate, name, temp, tunit, humidity, hunit):
    fan_mode = 'medium'
    data = { "entity_id" : climate , "fan_mode" : fan_mode }
    hass.services.call('climate', 'set_fan_mode', data)
    data = { "entity_id" : climate }
    hass.services.call('climate', 'turn_on', data)
    title = 'Aircon turn on - ' + name + '. Temp: ' + temp + tunit + '. Humidity: ' + humidity + hunit + '.'
    data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)

def turn_low_aircon(climate, name, temp, tunit, humidity, hunit):
    fan_mode = 'low'
    data = { "entity_id" : climate , "fan_mode" : fan_mode }
    hass.services.call('climate', 'set_fan_mode', data)
    title = 'Aircon turn low - ' + name + '. Temp: ' + temp + tunit + '. Humidity: ' + humidity + hunit + '.'
    data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)
    
def turn_off_aircon(climate, name, temp, tunit, humidity, hunit):
    data = { "entity_id" : climate }
    hass.services.call('climate', 'turn_off', data)
    title = 'Aircon turn low - ' + name + '. Temp: ' + temp + tunit + '. Humidity: ' + humidity + hunit + '.'
    data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)

# Get script variables

trigger_entity	    = data.get('trigger_entity') or 'NO_ENTITY'

debuginfo = 'Trigger entity test 1: ' + trigger_entity + '.'

if debug == 'on' : logger.error(debuginfo)

if trigger_entity == 'sensor.date__time' :
    trigger_entity = 'NO_ENTITY'

debuginfo = 'Trigger entity test 2: ' + trigger_entity + '.'
if debug2 == 'on' : logger.error(debuginfo)

# where specific trigger entity identified

if trigger_entity != 'NO_ENTITY' :
  
  if debug2 == 'on' : logger.error('if (1) condition. Trigger_entity == ' + trigger_entity + '.')
  
  for e in Entity :
      count = count + 1
      if e == trigger_entity :
          climate_id = climateEntity[count]
          temp_id = tempEntity[count]
          humidity_id = humidityEntity[count]
          occupancy_id = occupancyEntity[count]

# get temp and humidity and entity state now that we know the right entity
  state_climate		= hass.states.get(climate_id).state
  fn				= hass.states.get(climate_id).attributes.get('friendly_name')
  state_temp		= hass.states.get(temp_id).state
  tuom 				= hass.states.get(temp_id).attributes.get('unit_of_measurement')
  state_humidity	= hass.states.get(humidity_id).state
  huom 				= hass.states.get(humidity_id).attributes.get('unit_of_measurement')
  state_occupancy	= hass.states.get(occupancy_id).state
  dt 				= hass.states.get(climate_id).last_changed

# Debug section:

  if debug == 'on' : logger.error('Entity_ID: ' + climate_id + ' Climate: ' + state_climate)
  if debug == 'on' : logger.error('Entity_ID: ' + temp_id + ' Temperature: ' + state_temp)
  if debug == 'on' : logger.error('Entity_ID: ' + humidity_id + ' Humidity: ' + state_humidity)
  if debug == 'on' : logger.error('Entity_ID: ' + occupancy_id + ' Occupancy: ' + state_occupancy)
  
  res = occupancy_test(state_occupancy)
  if debug == 'on' : logger.error('occupancy_test:  return: ' + str(res) + '.')
  
  res = aa_pt_test(state_aa, state_pt)
  if debug == 'on' : logger.error('aa_pt_test:  return: ' + str(res) + '.')
  
  
  res = presence_test(climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test)
  if debug == 'on' : logger.error('aa_pt_test:  return: ' + str(res) + '.')
  
  res = occupancy_all_test(state_occupancy_all)
  if debug == 'on' : logger.error('occupancy_all_test:  return: ' + str(res) + '.')
  
  res = temperature_test(state_temp)
  if debug == 'on' : logger.error('temperature_test:  return: ' + res + '.')
  
  res = last_changed(now, dt, fsec = 900)
  if debug == 'on' : logger.error('last_changed:  return: ' + str(res) + '.')
  
  res = conditions_on_test(state_temp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy)
  if debug == 'on' : logger.error('conditions_on_test:  return: ' + str(res) + '.')
  
  res = conditions_low_test(state_temp, temperature_test)
  if debug == 'on' : logger.error('conditions_low_test:  return: ' + str(res) + '.')
  
  res = conditions_off_test(state_temp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy)
  if debug == 'on' : logger.error('conditions_off_test:  return: ' + str(res) + '.')

# run the conditions testing:
  
  conditions_on = conditions_on_test(state_temp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy)
  conditions_low = conditions_low_test(state_temp, temperature_test)
  conditions_off = conditions_off_test(state_temp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy)
  
  if debug2 == 'on' : logger.error('conditions_on_test:  return: ' + str(conditions_on) + '. conditions_low_test:  return: ' + str(conditions_low) + '. conditions_off_test:  return: ' + str(conditions_off) + '.')


# take action based on test results  

  if conditions_on == 1 and state_climate == 'off' :
      fan_mode = 'medium'
      data = { "entity_id" : climate_id , "fan_mode" : fan_mode }
      hass.services.call('climate', 'set_fan_mode', data)
      data = { "entity_id" : climate_id }
      hass.services.call('climate', 'turn_on', data)
      title = 'Aircon turn on - ' + fn + '. Temp: ' + state_temp + tuom + '. Humidity: ' + state_humidity + huom + '.'
      data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
      hass.services.call('notify', 'slack', data)
      if debug2 == 'on' : logger.error('conditions_on met.')
      
  elif conditions_low == 1 and conditions_off == 0 and state_climate != 'off' :
      fan_mode = 'low'
      data = { "entity_id" : climate_id , "fan_mode" : fan_mode }
      hass.services.call('climate', 'set_fan_mode', data)
      title = 'Aircon turn low - ' + fn + '. Temp: ' + state_temp + tuom + '. Humidity: ' + state_humidity + huom + '.'
      data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
      hass.services.call('notify', 'slack', data)
      if debug2 == 'on' : logger.error('conditions_low met.')
  
  elif conditions_off == 1 and state_climate != 'off' :
      data = { "entity_id" : climate_id }
      hass.services.call('climate', 'turn_off', data)
      title = 'Aircon turn low - ' + fn + '. Temp: ' + state_temp + tuom + '. Humidity: ' + state_humidity + huom + '.'
      data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
      hass.services.call('notify', 'slack', data)
      if debug2 == 'on' : logger.error('conditions_off met.')

  else:
      if debug2 == 'on' : logger.error('no conditions met.') 

# if trigger entity not identifed then loop through and check all aircon units
  
else: 
  if debug2 == 'on' : logger.error('Else (2) condition. Trigger_entity == ' + trigger_entity + '.')
  
  climateEntity = ['climate.master_bedroom', 'climate.master_bedroom']
  tempEntity = ['sensor.multisensor2_temperature', 'sensor.multisensor2_temperature']
  humidityEntity = ['sensor.multisensor2_relative_humidity', 'sensor.multisensor2_relative_humidity']
  occupancyEntity = ['binary_sensor.occupancy_mainbedroom', 'binary_sensor.occupancy_mainbedroom']

  for c in climateEntity :
      count = count + 1
      
      climate_id = climateEntity[count]
      temp_id = tempEntity[count]
      humidity_id = humidityEntity[count]
      occupancy_id = occupancyEntity[count]
      
      # get temp and humidity and entity state now that we know the right entity
      state_climate		= hass.states.get(climate_id).state
      fn				= hass.states.get(climate_id).attributes.get('friendly_name')
      state_temp		= hass.states.get(temp_id).state
      tuom 				= hass.states.get(temp_id).attributes.get('unit_of_measurement')
      state_humidity	= hass.states.get(humidity_id).state
      huom 				= hass.states.get(humidity_id).attributes.get('unit_of_measurement')
      state_occupancy	= hass.states.get(occupancy_id).state
      dt 				= hass.states.get(climate_id).last_changed

      conditions_on = conditions_on_test(state_temp, now, dt, presence_test, occupancy_test, temperature_test, last_changed, climate_id, state_aa, state_pt, state_occupancy_all, aa_pt_test, occupancy_all_test, state_occupancy)
      conditions_low = conditions_low_test(state_temp, temperature_test)
      conditions_off = conditions_off_test(state_temp, now, dt, occupancy_test, temperature_test, last_changed, state_occupancy)
  
      if debug2 == 'on' : logger.error('conditions_on_test:  return: ' + str(conditions_on) + '. conditions_low_test:  return: ' + str(conditions_low) + '. conditions_off_test:  return: ' + str(conditions_off) + '.')

  
      if conditions_on == 1 and state_climate == 'off' :
          fan_mode = 'medium'
          data = { "entity_id" : climate_id , "fan_mode" : fan_mode }
          hass.services.call('climate', 'set_fan_mode', data)
          data = { "entity_id" : climate_id }
          hass.services.call('climate', 'turn_on', data)
          title = 'Aircon turn on - ' + fn + '. Temp: ' + state_temp + tuom + '. Humidity: ' + state_humidity + huom + '.'
          data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
          hass.services.call('notify', 'slack', data)
          if debug2 == 'on' : logger.error('conditions_on met.')

      elif conditions_low == 1 and conditions_off == 0 and state_climate != 'off' :
          fan_mode = 'low'
          data = { "entity_id" : climate_id , "fan_mode" : fan_mode }
          hass.services.call('climate', 'set_fan_mode', data)
          title = 'Aircon turn low - ' + fn + '. Temp: ' + state_temp + tuom + '. Humidity: ' + state_humidity + huom + '.'
          data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
          hass.services.call('notify', 'slack', data)
          if debug2 == 'on' : logger.error('conditions_low met.')

      elif conditions_off == 1 and state_climate != 'off' :
          data = { "entity_id" : climate_id }
          hass.services.call('climate', 'turn_off', data)
          title = 'Aircon turn low - ' + fn + '. Temp: ' + state_temp + tuom + '. Humidity: ' + state_humidity + huom + '.'
          data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
          hass.services.call('notify', 'slack', data)
          if debug2 == 'on' : logger.error('conditions_off met.')

      else:
          if debug2 == 'on' : logger.error('no conditions met.')
          
          
    
    

