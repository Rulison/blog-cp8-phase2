import json
import os
import fnmatch

folders = [f for f in os.listdir('.') if fnmatch.fnmatch(f, 'user**')]
for folder in folders:
    path = folder + '/events-il.json'
    events_il_file = open(path)
    events_str = events_il_file.read()
    events_il_file.close()
    events = json.loads(events_str)
    for event in events:
        if event['workflowTemplateId'] == 5:
            event['workflowTemplateId'] = 2
    events_str = json.dumps(events, sort_keys = True, indent=4, separators=(',', ': '))
    new_events_il_file = open(folder + '/events_il_mod.json', 'w+')
    new_events_il_file.write(events_str)

for folder in folders:
    path = folder + '/events.json'
    events_il_file = open(path)
    events_str = events_il_file.read()
    events_il_file.close()
    events = json.loads(events_str)
    for event in events:
        if event['workflowTemplateId'] == 5:
            event['workflowTemplateId'] = 2
    events_str = json.dumps(events)
    new_events_il_file = open(folder + '/events_mod.json', 'w+')
    new_events_il_file.write(events_str)

    path = folder + '/events.json'
    events_file = open(path)
