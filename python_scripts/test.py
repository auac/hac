# Get time and states
now                 = datetime.datetime.now()
t                   = hass.states.get('sensor.time').state
timestamp           = "{}_{}_{}_{}_{}_{}_{}".format(
                      now.year, now.month, now.day, now.hour,
                      now.minute, now.second, now.microsecond)
count               = -1
debug				= 'off'
debug2				= 'on'
o = 1
l = 1

trigger_entity    = data.get('trigger_entity')
automation_lt  = data.get('automation_lt')
automation_now    = data.get('automation_now')
automation_diff    = data.get('automation_diff')

dt2                = datetime.datetime(2018 , 1, 1, 0, 0, 0, 0)

dt 				= hass.states.get('input_boolean.alarm_silence').last_changed
dtimestamp           = "{}_{}_{}_{}_{}_{}_{}".format(
                      now.year, now.month, now.day, now.hour,
                      now.minute, now.second, now.microsecond)


 
debuginfo = 'dt: ' + str( dt ) + '. \n'


 
debuginfo = debuginfo + 'dt2: ' + str( dt2 ) + '. \n'

debuginfo = debuginfo + 'dtimestamp: ' + str( dtimestamp ) + '. \n' 

def temperature() :
  res = 'below'
  return res

t = temperature()

res1 = now.isoweekday()

debuginfo = debuginfo + 'Datetime: ' + str( res1 ) + '. \n'


def test(o, t, l) :
  if ( o == 0 ) or ( t == 'below' and l == 1 ) or t == 'lowerbound' :
      return 1
  else :
      return 0

testresult = test(o, t, l)

debuginfo = debuginfo + 'testresult :' + str(testresult) + '. \n'


debuginfo = debuginfo + 'trigger_entity :' + str(testresult) + '. \n'

debuginfo = debuginfo + 'automation_lt :' + str(automation_lt) + '. \n'

debuginfo = debuginfo + 'automation_now :' + str(automation_now) + '. \n'

debuginfo = debuginfo + 'automation_diff :' + str(automation_diff) + '. \n'

logger.error(debuginfo)


# end of file