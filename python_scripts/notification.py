# Get time and settings
now                 = datetime.datetime.now()
t                   = hass.states.get('sensor.time').state
timestamp           = "{}_{}_{}_{}_{}_{}_{}".format(
                      now.year, now.month, now.day, now.hour,
                      now.minute, now.second, now.microsecond)
sending             = 'on'
send_image          = 0
count               = -1
aa                  = hass.states.get('input_boolean.presence_a').state

# Get script variables
target      = data.get('target') or '#info'
msg         = ''
color       = data.get('color') or 'good'
title       = data.get('message') or 'HA automation' 
text        = data.get('text') or (' @ ' + t)
entity_id   = data.get('entity_id') or 'ENTITY_IDError'
path        = data.get('path') or 'PATHError'
device_class= data.get('device_class') 

# check if image sending is required and 
# define the camera to take the image from

entitys = ['binary_sensor.main_door_sensor_sensor', 'binary_sensor.multisensor1_sensor']
cameras = ['camera.living_room_camera', 'camera.living_room_camera']

for entity in entitys :
    count = count + 1
    if entity == entity_id :
        send_image = send_image + 1
        camera_id  = cameras[count]

# create image file if image file required
    
if send_image == 1 :
    if entity_id == 'ENTITY_IDError' or path == 'PATHError' :
        text = text + ' ' + entity_id + ' ' + path
    else :
        filename = path + '/' + timestamp + entity_id + '.jpg' 			# filename key for service call               
        data = { "entity_id" : camera_id , "filename" : filename }
        hass.services.call('camera', 'snapshot', data )
#        while not os.path.exists(filename):
        time.sleep(5)

# Call service and send to target channel if specified (only if the target is not info / warn specified later)
if target != '#info' and target != '#warn' :
#    title = title + ' call 1. Target: ' + target 
    if send_image == 1 :
        data = { "target" : target , "message" : title , "title" : text , "data" : { "file" : { "path" : filename } } }
    else :
        data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)

# Call service and send to warning channel (or if aa not home):
if (
    device_class == 'connectivity' or device_class == 'door' or device_class == 'window' or 
    device_class == 'opening' or device_class == 'occupancy' or device_class == 'smoke') \
    or aa == 'off' \
    or entity_id == 'binary_sensor.multisensor1_sensor' \
    or target == '#warn' :
    
#    title = title + ' call 3. Target: ' + target
    target = '#warn'
    if send_image == 1 :
        data = { "target" : target , "message" : title , "title" : text , "data" : { "file" : { "path" : filename } } }
    else :
        data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)
    
# Call service and send to notification all the time
if sending == 'on' :
    target = '#info'
#    title = title + ' call 2. Target: ' + target
    if send_image == 1 :
        data = { "target" : target , "message" : title , "title" : text , "data" : { "file" : { "path" : filename } } }
    else :
        data = { "target" : target , "message" : msg , "data" : { "attachments" : [ { "color" : color , "title" : title , "text" : text } ] } }
    hass.services.call('notify', 'slack', data)
    
