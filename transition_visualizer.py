import json
import numpy as np
import scipy.misc as smp
import fnmatch
import os
import matplotlib.pyplot as plt


folders = [f for f in os.listdir('.') if fnmatch.fnmatch(f, 'user**')]

workflow_to_stats = {}
workflow_to_stats[1] = [0,0,0]
workflow_to_stats[2] = [0,0,0]

workflow_to_list = {}
workflow_to_list[1] = []
workflow_to_list[2] = []

for folder in folders:
    num_active = 0
    data_file = open(folder + '/events_il_mod.json')
    prev_event = None
    data = json.loads(data_file.read())
    for event in data:
        if prev_event == None:
            prev_event = event
            continue
        if event['workflowTemplateInstanceId'] == prev_event['workflowTemplateInstanceId'] and event['workflowTemplateId'] == prev_event['workflowTemplateId']:
            workflow_to_stats[prev_event['workflowTemplateId']][0] += 1
            workflow_to_list[prev_event['workflowTemplateId']].append(0)
        elif event['workflowTemplateId'] == prev_event['workflowTemplateId']:
            workflow_to_stats[prev_event['workflowTemplateId']][1] += 1
            workflow_to_list[prev_event['workflowTemplateId']].append(1)
        else:
            workflow_to_stats[prev_event['workflowTemplateId']][2] += 1
            workflow_to_list[prev_event['workflowTemplateId']].append(2)
        prev_event = event


for i in range(1,3):
    plt.hist(workflow_to_list[i])
    plt.show()
