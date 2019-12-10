import sys
import json
import copy

class BayesianNetwork(object):

	def __init__(self, structure, values, queries):
		# you may add more attributes if you need
		self.variables = structure["variables"]
		self.dependencies = structure["dependencies"]
		self.conditional_probabilities = values["conditional_probabilities"]
		self.prior_probabilities = values["prior_probabilities"]
		self.queries = queries
		self.answer = []
		self.network = {}

	def construct(self):
		# Add nodes to network
		for X in self.variables:
			self.network[X] = {}
			node = self.network.get(X)
			node["Child"] = []
			node["Parent"] = []
			node["CPT"] = []
		
		for X in self.variables:
		
			node = self.network.get(X)
			
			# Select minimal set of predecessors
			parents = self.dependencies.get(X)
			
			# If there is a parent
			if isinstance(parents, list):
			
				# For each parent
				while len(parents) > 0:
					
					p = parents.pop()
					
					# Link parent to X
					parent = self.network.get(p)
					parent.get("Child").append(X)
					
					if(parent in node.get("Parent")):
						continue
						
					node.get("Parent").append(p)
					
					#if isinstance(parent.get("Parent"), list):
					#	for pred in parent.get("Parent"):
					#		parents.append(pred)
			
				# Write CPT
				node["CPT"] = self.conditional_probabilities.get(X)
			
			else:
				# Write CPT
				node["CPT"] = self.prior_probabilities.get(X)




	def infer(self):
		# TODO: Your code here to answer the queries given using the Bayesian
		# network built in the construct() method.
		self.answer = []  # your code to find the answer
		# for the given example:
		# self.answer = [{"index": 1, "answer": 0.01}, {"index": 2, "answer": 0.71}]
		# the format of the answer returned SHOULD be as shown above.
		
		for query in self.queries:
			answer = self.make_query(query["given"], query["tofind"]);

			next_result = {}
			next_result["index"] = query["index"]
			next_result["answer"] = answer
			self.answer.append(next_result)

		return self.answer


	# multiple queries are made in the infer() method. this method handles one specific query.
	def make_query(self, given, to_find):
		pr_conjunction = self.get_event_probability(self.union(given, to_find))
		pr_condition = self.get_event_probability(given)
		return pr_conjunction / pr_condition



	# probability of an event
	def get_event_probability(self, event):
		all_worlds = self.generate_worlds(event)
		rv = 0

		for sq in all_worlds:
			rv += self.get_world_probability(sq)

		return rv


	# given an event, generate all possible worlds
	def generate_worlds(self, event):
		free_vars = []
		cur = [copy.deepcopy(event)]

		for var in self.variables:
			if not var in event.keys():
				free_vars.append(var)

		# loops through all variables that were not assigned in the provided event
		for var in free_vars:
			next = []

			for val in self.variables[var]:

				for specific_event in cur:
					more_specific_event = copy.deepcopy(specific_event)
					more_specific_event[var] = val
					next.append(more_specific_event)
				
			cur = next
		
		return cur


	# probability of a specific WORLD.
	def get_world_probability(self, state):
		rv = 1

		for var in state.keys():
			if var in self.prior_probabilities:
				rv *= self.prior_probabilities[var][state[var]]
				continue
			
			for cp_condition in self.conditional_probabilities[var]:
				match = True

				for cp_condition_var in cp_condition.keys():

					if cp_condition_var == "own_value":
						if cp_condition[cp_condition_var] != state[var]:
							match = False
							break
					elif cp_condition_var == "probability":
						continue
					else:
						if cp_condition[cp_condition_var] != state[cp_condition_var]:
							match = False
							break
				
				if not match:
					match = True
				else:
					rv *= cp_condition["probability"]
					break
		
		return rv


	# union of 2 dictionaries.
	def union(self, dict1, dict2):
		rv = {}

		for k in dict1.keys():
			rv[k] = dict1[k]
		
		for k in dict2.keys():
			rv[k] = dict2[k]
		
		return rv

	# You may add more classes/functions if you think is useful. However, ensure
	# all the classes/functions are in this file ONLY and used within the
	# BayesianNetwork class.

def main():
	# STRICTLY do NOT modify the code in the main function here
	if len(sys.argv) != 4:
		print ("\nUsage: python b_net_A3_xx.py structure.json values.json queries.json \n")
		raise ValueError("Wrong number of arguments!")

	structure_filename = sys.argv[1]
	values_filename = sys.argv[2]
	queries_filename = sys.argv[3]

	try:
		with open(structure_filename, 'r') as f:
			structure = json.load(f)
		with open(values_filename, 'r') as f:
			values = json.load(f)
		with open(queries_filename, 'r') as f:
			queries = json.load(f)

	except IOError:
		raise IOError("Input file not found or not a json file")

	# testing if the code works
	b_network = BayesianNetwork(structure, values, queries)
	b_network.construct()
	answers = b_network.infer()



if __name__ == "__main__":
	main()
