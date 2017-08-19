import argparse
import re
import json
import datetime
import os
import errno
import math

from sets import Set

parser = argparse.ArgumentParser(description="Convert swift CP8 results to json format.")
parser.add_argument('-i', '--input_file',
					help="Path to json.")


args = parser.parse_args()

input_file = open(args.input_file)
text = input_file.read()
events = json.loads(text)

normalizer = 0
pre_score = 0

for event in events:
    event_template_post = event['workflowTemplateIDPosterior']
    event_instance_post = event['workflowTemplateInstanceIDPosterior']

    correct_template = str(event['workflowTemplateId'])
    if correct_template == '2':
        correct_template = '5'
    print event_template_post
    print event['sequenceNumber']
    print correct_template
    pre_score += math.log(event_template_post[correct_template])
    normalizer += math.log(0.5)

score = float(normalizer)/pre_score
print "Score is " + str(score)
