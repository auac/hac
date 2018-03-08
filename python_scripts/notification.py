# Get time and settings
time                = hass.states.get('sensor.time').state
sending             = 'on'

# Get script variables
target      = data.get('target') or 'notification'
msg         = ''
color       = data.get('color') or 'good'
title       = data.get('message') or 'HA automation' 
text        = data.get('text') or (' @ ' + time)

# Call service
if sending == 'on' :
    data = { "target" : target, "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)
