import json
import argparse
import csv
import numpy
import math

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

def tStatistic(values):
	
	# Determines the t-statistic describing the difference between this dataset
	# and one with mean 0
	samples = numpy.array(values)
	n = len(values)
	# Sample mean
	x = samples.mean()
	# Sample std dev (corrected)
	s = samples.std(ddof=1)
	
	# Passes if no std deviation could be found
	if s==0: return 0
	
	t = x / (s / math.sqrt(n))
	return t

def main():
	args = parseArgs()
	
	# Reads files
	sentimentJson = json.load(open(args.s))
	genresJson = json.load(open(args.g))
	(sentimentList, genres) = joinDicts(sentimentJson, genresJson)
	
	# Sentiment regularization value
	VIRTUAL_COUNT = 10

	# Gets the average sentiment of songs from all genres
	counts = {}
	sentimentSums = {}
	sentimentLists = {}
	for i in xrange(len(genres)):
		for g in genres[i]:
			if g not in counts:
				counts[g] = 0
				sentimentSums[g] = 0
				sentimentLists[g] = []
			s = sentimentList[i]
			counts[g] += 1
			sentimentSums[g] += sentimentList[i]
			sentimentLists[g].append(s)
	
	sentiments = map(\
		lambda g: (g, sentimentSums[g] / float(counts[g])), \
		sentimentSums)
	
	regSentiments = map(\
		lambda g: (g, sentimentSums[g] / float(counts[g] + VIRTUAL_COUNT)), \
		sentimentSums)

	sentimentLists = {g: sentimentLists[g] for g in sentimentLists \
		if len(sentimentLists[g]) > 1}
	sentimentTstats = map(\
		lambda g: (g, tStatistic(sentimentLists[g])), \
		sentimentLists)
	
	sortedSentiments = sorted(sentiments, key=lambda s: -s[1])
	sortedRegSentiments = sorted(regSentiments, key=lambda s: -s[1])
	sortedSentimentTstats = sorted(sentimentTstats, key=lambda s: -s[1])
	
	# Outputs results
	outputFile = "genre_sentiment.txt"
	with open(outputFile, 'w+') as of:
		w = csv.writer(of)
		for s in sortedSentiments:
			w.writerow(s)
	
	# Outputs regularized results
	outputFile = "genre_sentiment_regularized.txt"
	with open(outputFile, 'w+') as of:
		w = csv.writer(of)
		for s in sortedRegSentiments:
			w.writerow(s)
	
	# Outputs t-statistic results
	outputFile = "genre_sentiment_tstats.txt"
	with open(outputFile, 'w+') as of:
		w = csv.writer(of)
		for s in sortedSentimentTstats:
			w.writerow(s)
	
if __name__=="__main__":
	main()