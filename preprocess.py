import json
import os
import fnmatch
import argparse

parser = argparse.ArgumentParser(description="Preprocesses data for BLOG.")
parser.add_argument('-t', '--training_dir',
                    help="Directory containing training folders of format user\d\d")
args = parser.parse_args()

base = args.training_dir

names = ['events-il', 'events-il-low', 'events-il-med', 'events-il-high']
mod = '-mod'
folders = [f for f in os.listdir(base) if fnmatch.fnmatch(f, 'user**')]
for folder in folders:
    for name in names:
        path = os.path.join(base, folder, name + '.json')
        events_il_file = open(path)
        events_str = events_il_file.read()
        events_il_file.close()
        events = json.loads(events_str)
        for event in events:
            if event['workflowTemplateId'] == 5:
                event['workflowTemplateId'] = 2
        events_str = json.dumps(events, sort_keys = True, indent=4, separators=(',', ': '))
        new_events_il_file = open(os.path.join(base, folder, name + mod + '.json'), 'w+')
        new_events_il_file.write(events_str)

for folder in folders:
    path = os.path.join(base, folder, 'events.json')
    events_il_file = open(path)
    events_str = events_il_file.read()
    events_il_file.close()
    events = json.loads(events_str)
    for event in events:
        if event['workflowTemplateId'] == 5:
            event['workflowTemplateId'] = 2
    events_str = json.dumps(events)
    new_events_il_file = open(os.path.join(base, folder, 'events-mod.json'), 'w+')
    new_events_il_file.write(events_str)
