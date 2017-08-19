import json
from sets import Set
import argparse
import os, os.path
import re
import errno

parser = argparse.ArgumentParser(description="Writes test data to blog file.")
parser.add_argument('-i', '--input_file',
					help="Path to model file.")
parser.add_argument('-o', '--output_dir',
					help="Directory to write models with test data.")
parser.add_argument('-t', '--test_files', type=str, nargs='+',
                    help='Paths to test files.')
parser.add_argument('-p', '--parse_file',
					help="Path to read auxiliary data structures from.")

args = parser.parse_args()

parse_name = args.parse_file
parse_file = open(parse_name)
parse_str = parse_file.read()
all_param_types = json.loads(parse_str)

excluded_params = ['FILE_IN', 'FILE_OUT']
dict_params = ['EMAIL_IN', 'EMAIL_OUT']
null_str = 'null0'


def stringify(item):
	return str(item).replace('\\', '\\\\')

def format_set(s):
	out = ''
	for item in s:
		out += item + ', '
	return out

def format_probs(s, probs):
	out = ''
	for item in s:
		out += item[2] + ' -> ' + str(probs[item])
		out += ', '
	return out[:-2]

# Taken from http://stackoverflow.com/a/600612/119527
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

# write blog file
def write_file(num_timesteps):
	input_file = open(args.input_file, 'r')
	output = input_file.read()
	output += '\n'

  	for param in all_param_types:
		output += 'random String ' + param + '_obs_table(Timestep t, WorkflowSlot ws) ~\n'
		output += '\tif t == @0 & currentSlot(t) != ws then "' + null_str + '"\n'
		output += '\telse if ws != currentSlot(t) then ' + param + '_obs_table(prev(t), ws)\n'
		output += '\telse\n'
  		if param in test_params.keys():
  			instances = test_params[param]
  		else:
  			instances = {}
  		full_instances = []
  		last_value = null_str
  		added_something = False
  		for i in range(num_timesteps):
			if i in instances.keys():
				output += '\t\t'
	  			if added_something:
	  				output += 'else '
	  			added_something = True
				output += 'if t == @' + str(i) + ' then "' + instances[i] + '"\n'
				last_value = instances[i]
			elif i == 0:
				added_something = True
				output += '\t\tif t == @0 then "' + null_str + '"\n'
		output += '\t\telse ' + param + '_obs_table(prev(t), ws)'
  		output += ';\n'
  		output += 'random String ' + param + '_obs(Timestep t) ~\n'
		output += '\t' + param + '_obs_table(t, currentSlot(t))\n'
		output += ';\n'
		output += '\n'

	output += '\n'

	for i in range(num_timesteps):
		output += 'obs state(@' + str(i) + ') = ' + state_list[i] + ';\n'
		for j in range(5):
			output += 'query state_table(@' + str(i) + ', WS[' + str(j) + ']);\n'
		output += 'obs valid(@' + str(i) + ') = true;\n'
		output += 'obs validInstance(@' + str(i) + ') = true;\n'
		output += 'obs validPosition(@' + str(i) + ') = true;\n'
	for i in range(num_timesteps):
		output += 'query get_workflow_type(@' + str(i) + ');\n'
		for j in range(5):
			output += 'query get_workflow_type_table(@' + str(i) + ', WS[' + str(j) + ']);\n'
	for i in range(num_timesteps):
		output += 'query instanceId(@' + str(i) + ');\n'
		for j in range(5):
			for k in range(2):
				output += 'query instanceTable(WS[' + str(j) + '], WT[' + str(k) + '], @' + str(i) + ');\n'
	for i in range(num_timesteps):
		output += 'query position(@' + str(i) + ');\n'
		for j in range(5):
			output += 'query position_table(@' + str(i) + ', WS[' + str(j) + ']);\n'
	for i in range(num_timesteps):
		output += 'query currentSlot(@' + str(i) + ');\n'
	for i in range(num_timesteps):
		output += 'query coin_hack(@' + str(i) + ');\n'

	for i in range(num_timesteps):
		for param in all_param_types:
			output += 'query ' + param + '_obs(@' + str(i) + ');\n'
			for j in range(5):
				output += 'query ' + param + '_obs_table(@' + str(i) + ', WS[' + str(j) + ']);\n'


	output_file_name = os.path.join(args.output_dir, test_name) + '.blog'
	mkdir_p(os.path.dirname(output_file_name))
	output_file = open(output_file_name, 'w')
	output_file.write(output)
	output_file.close()




test_files = args.test_files

for test_name in test_files:
	test_file = open(test_name)
	events = json.loads(test_file.read())
	state_list = []
	test_params = {} # dictionary mapping from parameter to dictionaries from index to value
	i = 0
	for event in events:
		state_list.append(event['type'])
		event_params = event['parameters']
		for param in event_params.keys():
			if param in dict_params:
				inner_params = event_params[param].keys()
				for inner_param in inner_params:
					value = event_params[param][inner_param]
					if value == None:
						value = 'None'
					modified_param = param + '_' + inner_param
					if modified_param in test_params.keys():
						test_params[modified_param][i] = value
					else:
						test_params[modified_param] = {i: value}
			else:
				if param in test_params.keys():
					test_params[param][i] = stringify(event_params[param])
				else:
					test_params[param] = {i: stringify(event_params[param])}
		i += 1
	num_timesteps = len(events)
	write_file(num_timesteps)
