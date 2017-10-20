import json
from sets import Set
import argparse
import os
import re

parser = argparse.ArgumentParser(description="Writes model to blog file.")
parser.add_argument('-t', '--training_dir',
					help="Directory containing training folders of format user\d\d")
parser.add_argument('-o', '--output_file',
					help="Where to write model.")
parser.add_argument('-p', '--param_file',
					help="Where to write auxiliary data structures computed here.")
args = parser.parse_args()


# (workflow template id, oldState, newState) to count
transition_counts = {}
# (workflow template id, oldState, newState) to list of param names that must match
transition_params = {}
# maps from (workflow id, workflow type id) to (latest action, parameters and values)
state = {}

# (oldTemplateId, newTemplateId, oldInstanceNum, newInstanceNum, oldAction, newAction, oldPosition, newPosition) to count
interleave_counts = {}

all_param_types = Set()

null_str = 'null0'

end_states = {}
end_counts = {}

middle_counts = {}
middle_end_probs = {}

max_workflow_type_id = 2
# Set of all possible actions, learned from training data.
actions = Set()

def full_match(match, s):
	return match != None and match.group(0) == s

path = args.training_dir
only_dirs = [f for f in os.listdir(path) if not os.path.isfile(os.path.join(path, f))]

patn = 'user\d\d'
prog = re.compile(patn)
training_dirs = [os.path.join(path,d) for d in only_dirs if full_match(prog.match(d), d)]

excluded_params = ['FILE_IN', 'FILE_OUT']
dict_params = ['EMAIL_IN', 'EMAIL_OUT']

same_type_count = 0
diff_type_count = 0

for name in training_dirs:
	file_name = os.path.join(name, 'events-mod.json')
	events_file = open(file_name)
	events = json.loads(events_file.read())
	for event in events:
		if event['workflowPosition'] == 'END':
			if event['workflowTemplateId'] in end_states.keys():
				end_states[event['workflowTemplateId']].add(event['type'])
			else:
				end_states[event['workflowTemplateId']] = Set([event['type']])

def get_event_id(event):
	return (event['workflowTemplateId'], event['workflowTemplateInstanceId'], event['type'], event['workflowPosition'])

il_names = ['events-il-mod.json', 'events-il-low-mod.json', 'events-il-med-mod.json', 'events-il-high-mod.json']
for name in training_dirs:
	for il_name in il_names:
		file_name = os.path.join(name, il_name)
		events_file = open(file_name)
		events = json.loads(events_file.read())
		prev_event = None
		for event in events:
			if prev_event is not None:
				key = get_event_id(prev_event) + get_event_id(event)
				if key in interleave_counts.keys():
					interleave_counts[key] += 1
				else:
					interleave_counts[key] = 1
			prev_event = event

def prev_key_equals(k1, k2):
	return k1[0] == k2[0] and k1[1] == k2[1] and k1[2] == k2[2] and k1[3] == k2[3]
interleave_probs = {}
for key in interleave_counts.keys():
	total = sum([interleave_counts[k] for k in interleave_counts.keys() if prev_key_equals(key, k)])
	interleave_probs[key] = float(interleave_counts[key])/total


for num in end_states.keys():
	states = end_states[num]
	for s in states:
		end_counts[(num, s)] = 0
		middle_counts[(num, s)] = 0

for name in training_dirs:
	file_name = os.path.join(name, 'events-mod.json')
	events_file = open(file_name)
	events = json.loads(events_file.read())
	prev_type = None
	prev_id = None
	for event in events:
		actions.add(event['type'])
		key = (event['workflowTemplateId'], event['type'])
		if key in middle_counts.keys():
			if event['workflowPosition'] == 'MIDDLE':
				middle_counts[key] += 1
			else:
				end_counts[key] += 1
		if prev_type != None:
			if event['workflowTemplateId'] == prev_type and event['workflowTemplateInstanceId'] == prev_id:
				same_type_count += 1
			else:
				diff_type_count += 1
		prev_type = event['workflowTemplateId']
		prev_id = event['workflowTemplateInstanceId']

		# New workflow instance
		if event['workflowPosition'] == 'START':
			# Learn how many workflow types there are (6).
			state[(event['workflowTemplateId'], event['workflowTemplateInstanceId'])] = (event['type'], event['parameters'])
			key = (event['workflowTemplateId'], None, event['type'])
			if key in transition_counts.keys():
				transition_counts[key] += 1
			else:
				transition_counts[key] = 1
		# Continuing workflow instance
		else:
			workflowId = event['workflowTemplateId']
			instanceId = event['workflowTemplateInstanceId']
			currentState = state[(workflowId, instanceId)]
			runningParams = currentState[1]
			newParams = event['parameters']
			for param in newParams.keys():
				# Learn what params exist.
				if param not in dict_params:
					all_param_types.add(param)
			param_check_list = []
			matchingParamNames = None
			for param in newParams.keys():
				if param in excluded_params:
					continue
				if param in dict_params:
					inner_params = tuple(newParams[param].keys())
					param_check_list.append((param,inner_params))
					for p in inner_params:
						all_param_types.add(param + '_' + p)
				else:
					param_check_list.append(param)
			for param in param_check_list:
				if type(param) == tuple:
					for dict_param in dict_params:
						if dict_param in runningParams.keys():
							inner_params = runningParams[dict_param].keys()
							for old_inner_param in inner_params:
								for new_inner_param in newParams[param[0]].keys():
									if runningParams[dict_param][old_inner_param] == newParams[param[0]][new_inner_param]:
										if matchingParamNames == None:
											matchingParamNames = (((param[0], new_inner_param) ,(dict_param, old_inner_param)),)
										else:
											matchingParamNames += (((param[0], new_inner_param) ,(dict_param, old_inner_param)),)
				else:
					for oldParam in runningParams.keys():
						if type(oldParam) == tuple:
							top_param = oldParam[0]
							inner_params = oldParam[1]

						if newParams[param] == runningParams[oldParam]:
							if matchingParamNames == None:
								matchingParamNames = ((param, oldParam),)
							else:
								matchingParamNames += ((param, oldParam),)


			for param, val in newParams.items():
				runningParams[param] = val
			key = (event['workflowTemplateId'], currentState[0], event['type'])
			if key in transition_params.keys():
				oldMatching = transition_params[key]
				oldMatchingSet = Set()
				if oldMatching == None:
					oldMatchingSet.add(None)
				else:
					for i in oldMatching:
						oldMatchingSet.add(i)
				newMatchingSet = Set()
				if matchingParamNames == None:
					newMatchingSet.add(None)
				else:
					for i in matchingParamNames:
						newMatchingSet.add(i)
				overlapSet = oldMatchingSet.intersection(newMatchingSet)
				overlap = ()
				for i in overlapSet:
					overlap += (i,)
				if overlap == (None,) or overlap == ():
					overlap = None
				transition_params[key] = overlap
			else:
				transition_params[key] = matchingParamNames

			if key in transition_counts.keys():
				transition_counts[key] += 1
			else:
				transition_counts[key] = 1
			state[(workflowId, instanceId)] = (event['type'], runningParams)

transition_totals = {}
for key in transition_counts:
	key2 = key[:2]
	if key2 in transition_totals:
		transition_totals[key2] += transition_counts[key]
	else:
		transition_totals[key2] = transition_counts[key]

for key in middle_counts.keys():
	middle_end_probs[key] = float(middle_counts[key])/(middle_counts[key] + end_counts[key])

transition_probs = {}
for key in transition_counts:
	transition_probs[key] = transition_counts[key]/float(transition_totals[key[:2]])

def stringify(item):
	return str(item).replace('\\', '\\\\')


def format_set(s):
	out = ''
	for item in s:
		out += item + ', '
	return out

def format_probs(s, probs):
	out = ''
	names = Set([i[2] for i in s])
	for item in s:
		out += item[2] + ' -> ' + str(probs[item])
		out += ', '
	# Now add every possible state as an option with a small probability,
	# so no unforseen transition leads to all particles having 0 weight.
	for action in actions:
		if action not in names:
			out += action + ' -> ' '0.01'
			out += ', '
	return out[:-2] #[:-2] to remove trailing ', '

# write blog file
def write_file():
	output_file = open(args.output_file, 'w')
	output = ''
	output += 'type WorkflowType; distinct WorkflowType WT[' + str(max_workflow_type_id) + '];\n'
	output += '\n'

	num_slots = 5
	output += 'type WorkflowSlot; distinct WorkflowSlot WS[' + str(num_slots) + '];'
	output += '\n'

	output += 'type Action;\n'
	output += 'distinct Action ' + format_set(actions) + 'Invalid, Start;\n'
	output += '\n'
	output += 'type Position;\n'
	output += 'distinct Position UNSTARTED, START, MIDDLE, END, Invalid_Position;\n'

	output += 'extern Boolean is_reply(String subject);'


	output += 'random Integer instanceTable(WorkflowSlot ws, WorkflowType w, Timestep t) ~ \n'
	output += '\tif t == @0 & get_workflow_type(t) == w & currentSlot(t) == ws then 1\n'
	output += '\telse if t == @0 then 0\n'
	output += '\telse if currentSlot(t) == ws & get_workflow_type(t) == w & position(t) == START then max({instanceTable(ws, w, prev(t)) for WorkflowSlot ws}) + 1\n'
	output += '\telse instanceTable(ws, w, prev(t))'
	output += ';\n'
	output += '\n'
	output += 'random Integer instanceId(Timestep t) ~ \n'
	output += '\tinstanceTable(currentSlot(t), get_workflow_type(t), t)\n'
	output += ';\n'
	output += '\n'
	output += 'random Integer instanceTablePrev(WorkflowSlot ws, WorkflowType w, Timestep t) ~ \n'
	output += '\tinstanceTable(ws, w, t)\n'
	output += ';\n'
	output += '\n'
	output += 'random Boolean validInstance(Timestep t) ~ \n'
	output += '\tinstanceId(t) != 0'
	output += ';\n'
	output += '\n'

	output += 'random Real coin_hack(Timestep t) ~ UniformReal(0,1);\n'
#0.6 same workflow, 0.2 existing workflow, 0.1 new workflow
	output += 'random WorkflowSlot currentSlot(Timestep t) ~\n'
	output += 'if t == @0 then\n'
	output += '\tUniformChoice({ws for WorkflowSlot ws})\n'
	output += 'else if coin_hack(t) < 0.6 then\n'
	output += '\tcurrentSlot(prev(t))'
	output += 'else if coin_hack(t) < 0.9 then\n'
	#output += '\tUniformChoice({ws for WorkflowSlot ws : position_table(prev(t), ws) == START | position_table(prev(t), ws) == MIDDLE & ws != currentSlot(prev(t)) })\n'
	output += '\tUniformChoice({ws for WorkflowSlot ws})\n'
	output += 'else\n'
	output += '\tUniformChoice({ws for WorkflowSlot ws})\n'
	#output += '\tUniformChoice({ws for WorkflowSlot ws : position_table(prev(t), ws) == END | position_table(prev(t), ws) == Invalid_Position})'
	output += ';\n'
	output += '\n'

	output += 'random WorkflowType get_workflow_type(Timestep t) ~\n'
	output += '\tget_workflow_type_table(t, currentSlot(t))\n'
	output += ';\n'
	output += '\n'

	output += 'random WorkflowType get_workflow_type_table(Timestep t, WorkflowSlot ws) ~\n'
	output += '\tif t == @0 then UniformChoice({wt for WorkflowType wt})\n'
	output += '\telse if currentSlot(t) == ws & position_table(prev(t), ws) == END then UniformChoice({wt for WorkflowType wt})\n'
	output += '\telse get_workflow_type_table(prev(t), ws)\n'
	output += ';\n'
	output += '\n'

	output += 'random Position position(Timestep t) ~\n'
	output += '\tposition_table(t, currentSlot(t))\n'
	output += ';\n'
	output += '\n'
	# position function -----------------------
	output += 'random Position position_table(Timestep t, WorkflowSlot ws) ~ \n'
	output += '\tif t == @0 & ws == currentSlot(@0) then START\n'
	output += '\telse if t == @0 then UNSTARTED\n'
	output += '\telse if ws != currentSlot(t) then position_table(prev(t), ws)\n'
	output += '\telse if position_table(prev(t), ws) == UNSTARTED & state(t) == ReceiveEmail & !is_reply(EMAIL_IN_Subject_obs(t)) then START\n'
	output += '\telse if position_table(prev(t), ws) == START then MIDDLE\n'
	output += '\telse if position_table(prev(t), ws) == MIDDLE then\n'
	for wf in range(max_workflow_type_id):
		if wf == 0:
			output += '\t\tif get_workflow_type(t) == WT[' + str(wf) + '] then\n'
		else:
			output += '\t\telse if get_workflow_type(t) == WT[' + str(wf) + '] then\n'
		cur_keys = [k for k in middle_end_probs.keys() if k[0] == wf+1]
		for key in cur_keys:
			state = key[1]
			if key == cur_keys[0]:
				output += '\t\t\tif state(t) == ' + state + ' then\n'
			else:
				output += '\t\t\telse if state(t) == ' + state + ' then\n'
			output += '\t\t\t\tCategorical({MIDDLE -> ' + str(middle_end_probs[key]) + ', END -> ' + str(1 - middle_end_probs[key]) + '})\n'
		output += '\t\t\telse Categorical({MIDDLE -> 0.99, END -> 0.01})\n' # for robustness, instead of just MIDDLE
	output += '\t\telse Invalid_Position\n'
	output += '\telse if state(t) == ReceiveEmail & !is_reply(EMAIL_IN_Subject_obs(t)) then\n'
	output += '\t\tSTART\n'
	output += '\telse\n'
	output += '\t\tInvalid_Position\n'
	output += ';\n'
	output += 'random Boolean validPosition(Timestep t) ~\n'
	output += '\tposition(t) != Invalid_Position\n'
	output += ';\n'
	output += '\n'

	output += 'random Action state_table(Timestep t, WorkflowSlot ws) ~\n'
	output += '\tif t == @0 & currentSlot(t) == ws then ReceiveEmail\n'
	output += '\telse if t == @0 then Invalid\n'
	output += '\telse if ws != currentSlot(t)\n'
	output += '\t\tthen state_table(prev(t), ws)\n'
	output += '\telse if state_table(prev(t), ws) == Invalid | position_table(prev(t), ws) == END\n'
	output += '\t\tthen ReceiveEmail\n'
	sorted_keys = transition_probs.keys()
	sorted_keys.sort(key=lambda x: x[0])
	for w in range(max_workflow_type_id):
		output += '\telse if get_workflow_type(t) == WT[' + str(w)+ '] then\n'
		# get all states this workflow instances can be
		s = Set()
		# get all transitions found for this workflow
		keys = [key for key in sorted_keys if key[0] - 1 == w]
		for key in keys:
			if key[1] != None:
				s.add(key[1])
		added = False
		for state in s:
			cur_keys = [key for key in keys if key[1] == state]
			if not added:
				output += '\t\tif state_table(prev(t), ws) == ' + state + ' then\n'
			else:
				output += '\t\telse if state_table(prev(t), ws) == ' + state + ' then\n'
			added = True
			output += '\t\t\t\tCategorical({' + format_probs(cur_keys, transition_probs) + '})\n'
		output += '\t\telse Invalid\n'
	output += '\telse Invalid\n'
	output += ';\n'
	# state function ------------------
	output += 'random Action state(Timestep t) ~\n'
	output += '\tstate_table(t, currentSlot(t))\n'
	output += ';\n'
	output += '\n'

	#TODO: fix for phase 2
	# valid function -------------------
	output += 'random Boolean valid(Timestep t) ~ \n'
	output += '\tif t == @0 then true\n'
	output += '\telse if position(t) == START then true\n'
	for w in range(max_workflow_type_id):
		output += '\telse if get_workflow_type(t) == WT[' + str(w) + '] then\n'
		s = Set()
		from_keys = [key for key in sorted_keys if key[0] - 1 == w]
		for key in from_keys:
			if key[1] != None:
				s.add(key[1])
		first_state = True
		for state in s:
			output += '\t\t'
			if not first_state:
				output += 'else '
			first_state = False
			output += 'if state_table(prev(t), currentSlot(t)) == ' + state + ' then\n'
			#output += 'if prev_state(last_occurrence(prev(t), currentSlot(t)), currentSlot(t)) == ' + state + ' then\n'
			to_keys = [key for key in from_keys if key[1] == state]
			for t in to_keys:
				output += '\t\t\t'
				if t != to_keys[0]:
					output += 'else '
				output += 'if state(t) == ' + t[2] + ' & '
				params = transition_params[(w+1, state, t[2])]
				added_something = False
				if params == None or params == ():
					output += 'true\n'
					output += '\t\t\t\tthen true\n'
					continue
				if added_something:
					output += ' & '
				for param in params:
					if param != params[0]:
						output += ' & '
					if type(param[0]) == tuple:
						output += param[0][0] + '_' + param[0][1] + '_obs(t) == ' + param[1][0] + '_' + param[1][1] + '_obs_table(prev(t), currentSlot(t)) & ' + param[1][0] + '_' + param[1][1] + '_obs_table(prev(t), currentSlot(t)) != "' +null_str + '" '
					else:
						output += param[0] + '_obs(t) == ' + param[1] + '_obs_table(prev(t), currentSlot(t)) & ' + param[1] + '_obs_table(prev(t), currentSlot(t)) != "' + null_str + '" '
					added_something = True
				output += '\n'
				output += '\t\t\t\t'
				output += ' then true\n'
			output += '\t\t\telse false\n'
		output += '\t\telse false\n'
	output += ';\n'

	output_file.write(output)
	output_file.close()

write_file()

param_name = args.param_file
param_lst = [p for p in all_param_types]
param_str = json.dumps(param_lst)
param_file = open(param_name, 'w')
param_file.write(param_str)
param_file.close()
