import argparse
import re
import json
import datetime
import os
import errno

from sets import Set

parser = argparse.ArgumentParser(description="Convert swift CP8 results to json format.")
parser.add_argument('-i', '--input_file',
					help="Path to swift output.")
parser.add_argument('-o', '--output_file',
					help="Path to write json file to.")
parser.add_argument('-t', '--test_file',
					help="Path to test events file.")

# Taken from http://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# XXX Need to parse: workflow type, instance, position

args = parser.parse_args()

input_file = args.input_file
input_str = open(input_file, 'r').read()
patn = '.*query : get_workflow_type(.*)>> query : state.*'
prog = re.compile(patn, re.DOTALL)
result = prog.match(input_str)

mkdir_p(os.path.dirname(args.output_file))
output_file = open(args.output_file, 'w')

test_file = open(args.test_file, 'r')
test_str = test_file.read()
events = json.loads(test_str)

output_events = events[:]

num_timesteps = len(events)

num_workflows = 2

# workflow id to (start index, timestamp)
workflow_to_timestamp = {}
for i in range(num_workflows):
	workflow_to_timestamp[i] = []

positions = ['START', 'MIDDLE', 'END']

for i in range(0, num_timesteps):
	event = output_events[i]
	event['workflowTemplateIDPosterior'] = {}
	event['workflowTemplateInstanceIDPosterior'] = {}
	event['workflowPositionPosterior'] = {}
	#event['sequenceNumber'] = i + 1

	start_str = '>> query : get_workflow_type(@' + str(i) + ')'
	end_str = '>> query : get_workflow_type_table(@' + str(i) + ', WS[0])'

	start = input_str.find(start_str)
	end = input_str.find(end_str)
	cur_str = input_str[start + len(start_str):end]

	lines = cur_str.split('\n')
	for j in range(len(lines)):
		patn = 'WT\[(\d)\] -> (\d\.\d*)'
		prog = re.compile(patn)
		result = prog.match(lines[j])
		if result == None:
			continue
		num = int(result.group(1))
		prob = float(result.group(2))
		if num == 1:
			event['workflowTemplateIDPosterior']['5'] = prob
		else:
			event['workflowTemplateIDPosterior']['1'] = prob

	start_str = '>> query : instanceId(@' + str(i) + ')'
	end_str = '>> query : instanceTable(WS[0], WT[0], @' + str(i) + ')'

	start = input_str.find(start_str)
	end = input_str.find(end_str)
	cur_str = input_str[start + len(start_str):end]
	lines = cur_str.split('\n')[1:-1]

	for j in range(len(lines)):
		patn = '(\d*) -> (\d\.\d*)'
		prog = re.compile(patn)
		result = prog.match(lines[j])
		if result == None:
			print lines
		num = int(result.group(1))
		prob = float(result.group(2))
		event['workflowTemplateInstanceIDPosterior'][num] = prob

	start_str = '>> query : position(@' + str(i) + ')'
	end_str = '>> query : position_table(@' + str(i) + ', WS[0])'

	start = input_str.find(start_str)
	end = input_str.find(end_str)
	cur_str = input_str[start + len(start_str):end]
	lines = cur_str.split('\n')

	for j in range(len(lines)):
		patn = '([A-Z]*) -> (\d\.\d*)'
		prog = re.compile(patn)
		result = prog.match(lines[j])
		if result == None:
			continue
		pos = result.group(1)
		prob = float(result.group(2))
		event['workflowPositionPosterior'][pos] = prob

output_file.write(json.dumps(output_events, indent=2))

output_file.close()
test_file.close()
