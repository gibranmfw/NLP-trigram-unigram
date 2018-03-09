import sys
import numpy as np
import pandas as pd

def unpack(testpath):
	try:
		infile = open(testpath, 'r')
		
		sentences = []
		
		for line in infile:
			if "\n" in line:
				line = line[0:len(line)-1]
			sentences.append(line.strip().split(" "))
		
		return sentences
		
	except IOError:
		sys.exit("Couldn't open file at %s" % (testpath))

def viterbi(line, transition, emission, tagsc, wordsc):
	l = len(line)
	best_score = []
	best_edge = []
	
	best_score.append({"<s> <s>":0})
	best_edge.append({"<s> <s>":None})
	
	
	#Forward Steps
	for i in range(0, l):
		for prev in list(transition):
			last = ""
			for next in list(tagsc['count'].keys()):
				# print("Best score at " + str(i) + " " + str(best_score))
				# print("Best edge at " + str(i) + " " + str(best_edge))
				# print()
				if prev in best_score[i] and transition[prev][next] != 0:
					# PLEASE CHECK THIS IF IT'S WRONG
					print("Best score at " + str(i) + " " + str(best_score))
					print("Best edge at " + str(i) + " " + str(best_edge))
					# print()
					print("Menghitung Skor " + str(line[i]) + " dengan tag " + str(next))
					# print()
					
					if(line[i] in emission[next] and emission[next][line[i]] != 0.0):
						# print(transition[next][prev])
						# print(tagsc["count"][prev]/tagsc["count"].sum())
						# score = best_score[i][prev] + (np.log2(transition[next][prev]/(tagsc["count"][prev]/tagsc["count"].sum())) * -1) + (np.log2(emission[next][line[i]]/(tagsc["count"][next]/tagsc["count"].sum())) * -1)
						score = best_score[i][prev] + (np.log2(transition[prev][next]) * -1) + (np.log2(emission[next][line[i]]) * -1)
						# print(score)
					else:
						if(line[i] not in emission[next]):
							# score = -1
							score = best_score[i][prev] + (np.log2(transition[prev][next]) * -1)
						else:
							score = best_score[i][prev] + (np.log2(transition[prev][next]) * -1) + (np.log2(emission[next][line[i]]) * -1)
							# score = 0
						# print(score)
					
					print("Score : " + str(score))
					tag1, tag2 = prev.split(" ")
					next2 = "{} {}".format(tag2, next)
					print(best_score)
					print(last)
					# print(len(best_score))
					if next == '</s>':
						pass
					elif score == -1:
						best_score.append({'XX': score})
						best_edge.append({'XX': prev})
						last = 'XX'
						break
					elif i+1 == len(best_score):
						best_score.append({next2: score})
						best_edge.append({next2: prev})
						last = next2
					elif best_score[i+1][last] > score and next != '</s>':
						print("Skor menggunakan tag {} lebih kecil daripada {} ({} < {}), mereplace".format(next, last, score, best_score[i+1][last]))
						# print(str(best_score[i+1][last]) + " " + str(score))
						best_score[i+1] = {next2: score}
						best_edge[i+1] = {next2: prev}
						last = next2
					print()
	
	best_score.append({"</s> </s>":0})
	best_edge.append({"</s> </s>":None})
					
	# print(best_score)
	# print(best_edge)
	
	return best_edge
	
	#Backward Steps
	# tags = []
	# next_edge = best_edge[l]["</s>"]
	
	# i = l
	# while next_edge != best_edge[0]["<s>"]:
		# best_edge[i-1]
	
	# TODO: Backward Steps
	# https://warstek.com/2018/01/22/part-speech-tagger-untuk-bahasa-indonesia-menggunakan-konsep-hidden-markov-model-hmm-dan-algoritma-viterbi/
	
		
def tag(testpath, transitionpath, emissionpath, tagsc, wordsc):
	sentences = unpack(testpath)
	transition = pd.read_csv(transitionpath, index_col=0)
	emission = pd.read_csv(emissionpath, index_col=0)
	tagsc = pd.read_csv(tagsc, index_col=0)
	wordsc = pd.read_csv(wordsc, index_col=0)
	
	x= ""
	for line in sentences:
		result = viterbi(line, transition, emission, tagsc, wordsc)
		x += "Sentences:	" + ' '.join(line) + "\nTag:		"
		for s in result:
			for k, v in s.items():
				_, k = k.split(' ')
				x += str(k)+" "
		x += "\n" 
	
	print("RESULTS\n" + x)
	# print("DISCLAIMER:")
	# print("The words that doesn't included in the corpus will be automatically assigned to XX")
	# print(sentences)

def main():
	argv = sys.argv[1:]

	if len(argv) < 5:
		print("""
	HMM POS Tagger generator.

	Usage: %s testpath transitionpath emissionpath tagscount wordscount
	""" % sys.argv[0])
		sys.exit(1)

	test = argv.pop(0)
	transition = argv.pop(0)
	emission = argv.pop(0)
	tagscount = argv.pop(0)
	wordscount = argv.pop(0)

	tag(test, transition, emission, tagscount, wordscount)
	
if __name__ == "__main__":
	main()
