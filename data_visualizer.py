import json
import numpy as np
import scipy.misc as smp
import fnmatch
import os


folders = [f for f in os.listdir('.') if fnmatch.fnmatch(f, 'user**')]
folders = ['user04']

workflows = []
id_to_row = {}
row_counter = 0

active_workflows = {}
alt_hist = []
five_hist = []

for folder in folders:
    num_active = 0
    data_file = open(folder + '/events-il.json')
    data = json.loads(data_file.read())
    for event in data:
        event_pos = event['workflowPosition']
        if event_pos == 'START':
            num_active += 1
        elif event_pos == 'END':
            num_active -= 1
        event_id = (event['workflowTemplateId'], event['workflowTemplateInstanceId'])
        workflows.append(event_id)
        if event_id not in id_to_row.keys():
            id_to_row[event_id] = row_counter
            row_counter += 1
        if num_active not in active_workflows.keys():
            active_workflows[num_active] = 1
        else:
            active_workflows[num_active] += 1
        alt_hist.append(num_active)


data = np.zeros((row_counter, len(workflows), 3), dtype=np.uint8)

i=0
for event_id in workflows:
    data[id_to_row[event_id], i] = (255, 255, 255)
    i += 1

histo =[]
for num in sorted(active_workflows.keys()):
    histo.append(active_workflows[num])

import matplotlib.pyplot as plt

plt.imshow(data, aspect='auto', interpolation='none')

plt.show()
plt.hist(alt_hist)
plt.show()
