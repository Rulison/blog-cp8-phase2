import json
import numpy as np
import scipy.misc as smp
import fnmatch
import os


folders = ['out/user04/USER-04.map.json']

workflows = []
id_to_row = {}
row_counter = 0

active_workflows = {}
alt_hist = []
five_hist = []

for folder in folders:
    data_file = open(folder)
    data = json.loads(data_file.read())
    for event in data:
        event_template_post = event['workflowTemplateIDPosterior']
        event_instance_post = event['workflowTemplateInstanceIDPosterior']
        best_template = -1
        template_prob = 0
        best_instance = -1
        instance_prob = 0
        for key in event_template_post.keys():
            if event_template_post[key] > template_prob:
                best_template = key
                template_prob = event_template_post[key]
        for key in event_instance_post:
            if event_instance_post[key] > instance_prob:
                best_instance = key
                instance_prob = event_instance_post[key]

        event_id = (best_template, best_instance)
        workflows.append(event_id)
        if event_id not in id_to_row.keys():
            id_to_row[event_id] = row_counter
            row_counter += 1


data = np.zeros((row_counter, len(workflows), 3), dtype=np.uint8)

i=0
for event_id in workflows:
    data[id_to_row[event_id], i] = (255, 255, 255)
    i += 1

import matplotlib.pyplot as plt

plt.imshow(data, aspect='auto', interpolation='none')

plt.show()
