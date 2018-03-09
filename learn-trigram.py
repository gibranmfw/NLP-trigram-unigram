# Pseudocode for this code can be achieved in
# https://warstek.com/2018/01/22/part-speech-tagger-untuk-bahasa-indonesia-menggunakan-konsep-hidden-markov-model-hmm-dan-algoritma-viterbi/

import sys
import numpy as np
import pandas as pd

def unpack(filename): # Returns a list of words and parallel list of tags

	try:
		infile = open(filename, 'r')

		temp = {}
		transition = {}
		emission = {}
		tagscount = {}
		wordscount = {}
		tagscount["<s>"] = 0
		tagscount["</s>"] = 0
		
		for line in infile:
			previous = "<s>"
			tagscount["<s>"] += 1
			sentences = line.strip().split(' ')
			for i in range(1, len(sentences)):
				(word, tag) = sentences[i - 1].split('/')
				(word2, tag2) = sentences[i].split('/')

				if '{} {} {}'.format(previous, tag, tag2) in transition:
					transition['{} {} {}'.format(previous, tag, tag2)] += 1
				else:
					transition['{} {} {}'.format(previous, tag, tag2)] = 1

				# Count the emission
				if '{} {}'.format(word, tag) in emission:
					emission['{} {}'.format(word, tag)] += 1
				else:
					emission['{} {}'.format(word, tag)] = 1
				
				if tag in tagscount:
					tagscount[tag] += 1
				else:
					tagscount[tag] = 1				

				if word in wordscount:
					wordscount[word] += 1
				else:
					wordscount[word] = 1
								
				previous = tag
				
				if '{} {} </s>'.format(previous, tag) in transition:
					transition['{} {} </s>'.format(previous, tag)] += 1
				else:
					transition['{} {} </s>'.format(previous, tag)] = 1
			tagscount["</s>"] += 1
	
	except IOError:
		sys.exit("Couldn't open file at %s" % (filename))

	infile.close()
	#print("T: {}\n\nE: {}\n\nTgsCount: {}\n\nWrdsCount: {}\n\n".format(transition, emission, tagscount, wordscount))
	return transition, emission, tagscount, wordscount

def count_twotag(transition):
	twotag = {}
	for key in transition.keys():
		tag1, tag2, tag3 = key.split(" ")
		if("{} {}".format(tag1, tag2) not in twotag):
			twotag["{} {}".format(tag1, tag2)] = transition["{} {} {}".format(tag1, tag2, tag3)]
		else:
			twotag["{} {}".format(tag1, tag2)] += transition["{} {} {}".format(tag1, tag2, tag3)]
	return twotag

def count_probability(transition, emission, tagscount, wordscount):
	twotag = count_twotag(transition)
	transition_probability = transition
	emission_probability = emission
	v = len(set(wordscount))
	
	# Count the probability of transition
	for tag1 in list(tagscount.keys()):
		for tag2 in list(tagscount.keys()):
			for tag3 in list(tagscount.keys()):
				if("{} {} {}".format(tag1, tag2, tag3) in transition):
					transition_probability["{} {} {}".format(tag1, tag2, tag3)] = round((transition["{} {} {}".format(tag1, tag2, tag3)] + 1) / (twotag["{} {}".format(tag1, tag2)]+v), 5)
				else:
					transition_probability["{} {} {}".format(tag1, tag2, tag3)] = round(1/(tagscount[tag1]+v), 5)
		
	# Count the probability of emission
	for word in list(wordscount.keys()):
		for tag in list(tagscount.keys()):
			if("{} {}".format(word, tag) in emission):
				emission_probability["{} {}".format(word, tag)] = round((emission["{} {}".format(word, tag)] + 1) / (tagscount[tag] + v), 5)
			else:
				emission_probability["{} {}".format(word, tag)] = round(1/(tagscount[tag]+v), 5)
	
	#print("Tp: {}\n\nEp: {}\n\n".format(transition_probability, emission_probability))
	return transition_probability, emission_probability

def prettify(transition_probability, emission_probability, tagscount, wordscount):
	transition_pretty = []
	emission_pretty = []
	
	for tag1 in list(tagscount.keys()):
		line = []
		for tag2 in list(tagscount.keys()):
			for tag3 in list(tagscount.keys()):
				line.append(transition_probability["{} {} {}".format(tag1, tag2, tag3)])
		transition_pretty.append(line)
	
	for word in list(wordscount.keys()):
		line = []
		for tag in list(tagscount.keys()):
			line.append(emission_probability["{} {}".format(word, tag)])
		emission_pretty.append(line)
	
	#print("Tpret: {}\n\nEpret: {}\n\n".format(transition_pretty, emission_pretty))
	return transition_pretty, emission_pretty

def makeColumn(tagscount):
	column = []
	for tag1 in list(tagscount):
		for tag2 in list(tagscount):
			if "{} {}".format(tag1, tag2) not in column:
				column.append("{} {}".format(tag1, tag2))
	return column

def export_data_to_csv(transition_pretty, emission_pretty, tagscount, wordscount):
	tp = np.array(transition_pretty)
	ep = np.array(emission_pretty)
	
	column = makeColumn(tagscount)
	dftp = pd.DataFrame(data=tp, index=list(tagscount.keys()), columns=column)
	dfep = pd.DataFrame(data=ep, index=list(wordscount.keys()), columns=list(tagscount))
	
	dftp.to_csv("transition-laplace-lemmatization.csv", sep=",", encoding="utf-8")
	dfep.to_csv("emission-laplace-lemmatization.csv", sep=",", encoding="utf-8")
		
	CSV = ",count\n"
	for k,v in tagscount.items():
		line = "{},{}\n".format(k, v)
		CSV+=line
	with open("tagscount-laplace-lemmatization.csv", "w") as file:
		file.write(CSV)
		
	CSV = ",count\n"
	for k,v in wordscount.items():
		line = "{},{}\n".format(k, v)
		CSV+=line
	with open("wordscount-laplace-lemmatization.csv", "w") as file:
		file.write(CSV)
	
	print("CSV of the Transition and Emission Probability has been successfully exported!")
	

def traindata(trainingfile):
	(transition, emission, tagscount, wordscount) = unpack(trainingfile)
	(transition_probability, emission_probability) = count_probability(transition, emission, tagscount, wordscount)
	(transition_pretty, emission_pretty) = prettify(transition_probability, emission_probability, tagscount, wordscount)
	export_data_to_csv(transition_pretty, emission_pretty, tagscount, wordscount)

def main():
	argv = sys.argv[1:]

	if len(argv) < 1:
		print("""
	HMM POS Tagger Learner.

	Usage: %s trainpath
	""" % sys.argv[0])
		sys.exit(1)

	train = argv.pop(0)

	traindata(train)
	
if __name__ == "__main__":
	main()
