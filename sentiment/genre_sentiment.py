import json
import argparse
import csv

def joinDicts(d1, d2):
	# Inner joins two dicts on their keys
	join = ([],[])
	for k in d1:
		if k in d2:
			join[0].append(d1[k])
			join[1].append(d2[k])
	return join

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-s', default="./lyric_sentiment.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	return parser.parse_args()

def main():
	args = parseArgs()
	
	# Reads files
	sentimentJson = json.load(open(args.s))
	genresJson = json.load(open(args.g))
	(sentimentList, genres) = joinDicts(sentimentJson, genresJson)

	# Gets the average sentiment of songs from all genres
	counts = {}
	sentiments = {}
	for i in xrange(len(genres)):
		for g in genres[i]:
			if g not in counts:
				counts[g] = 0
				sentiments[g] = 0
			counts[g] += 1
			sentiments[g] += sentimentList[i]
	for g in sentiments:
		sentiments[g] /= float(counts[g])
	
	sortedSentiments = sorted(sentiments.items(), key=lambda s: -s[1])
	
	# Outputs results
	outputFile = "genre_sentiment.txt"
	with open(outputFile, 'w+') as of:
		w = csv.writer(of)
		for s in sortedSentiments:
			print s
			w.writerow(s)

if __name__=="__main__":
	main()