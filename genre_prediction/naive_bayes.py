# Performs K nearest neighbors classification on the lyrics dataset

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from sklearn.naive_bayes import BernoulliNB
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import cross_validation
from sklearn.preprocessing import MultiLabelBinarizer
import json
import argparse
import random
from basic_tokenizer import Tokenizer

def joinDicts(d1, d2):
	# Inner joins two dicts on their keys
	join = ([],[])
	for k in d1:
		if k in d2:
			join[0].append(d1[k])
			join[1].append(d2[k])
	return join

def extractFeatures(lyrics, tokenizer, binary=True):
	v = CountVectorizer(binary=binary, lowercase=True, tokenizer=tokenizer)
	return v.fit_transform(lyrics)
	
def vectorizeLabels(genres):
	return MultiLabelBinarizer().fit_transform(genres)

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', default=10, help='Number of neighbors to train the classifier on')
	parser.add_argument('-l', default="../data/lyrics.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	parser.add_argument('-c', default=4, help='Number of folds in the cross-validation')
	parser.add_argument('-s', default="../util_data/stopwords.txt", help='Path to stopwords file')
	return parser.parse_args()

def loadStopwords(filename):
	# Loads the stop words
	stopwords = open(filename).readlines()
	stopwords = map(lambda l: l.strip(), stopwords)
	return stopwords

def main():
	args = parseArgs()
	
########################################
	# Features settings 
	stemWords = False
	binary = True
	removeStopwords = False

########################################

	# Labels = first listed genres
	lyricsFile = args.l
	genresFile = args.g
	stopwordsFile = args.s
	
	try:
		n = int(args.n)
		c = int(args.c)
	except ValueError:
		print e
		return
	
	# Loads the data files
	lyrics = json.load(open(lyricsFile))
	genres = json.load(open(genresFile))
	
	# Filters empty lyric strings and genre lists
	lyrics = {k: lyrics[k] for k in lyrics if len(lyrics[k])!=0}
	genres = {k: genres[k] for k in genres if len(genres[k])!=0}
	
	# Returns two lists of corresponding lyric-genre pairs
	(lyrics, genres) = joinDicts(lyrics, genres)
	numSongs = len(lyrics)
	
	# Extracts features (lyrics)
	t = Tokenizer(stem=stemWords)
	if removeStopwords:
		t.addStopwords(loadStopwords(stopwordsFile))
	
	features = extractFeatures(lyrics, t, binary=binary)
	
	# Extracts labels
	singleLabels = map(lambda g: g[0], genres)
	multiLabels = vectorizeLabels(genres)
	
	# Shuffles the labels to randomize them
	randomSingleLabels = list(singleLabels)
	random.shuffle(randomSingleLabels)
	
	# Creates the classifier
	nb = BernoulliNB(binarize=None)
		
	# Cross-validation: Single Labels
	singleGenreScores = cross_validation.cross_val_score( \
		nb, features, singleLabels, cv=c, scoring='accuracy' \
	)
	
	# Cross-validation: Random single labels
	singleGenreRandomScores = cross_validation.cross_val_score( \
		nb, features, randomSingleLabels, cv=c, scoring='accuracy' \
	)

	# Prints statistics
	print "Number of songs:", numSongs
	print "-- Single-genre model --"
	print "Mean:   ", singleGenreScores.mean()
	print "Std dev:", singleGenreScores.std()
	print "-- Random genre model --"
	print "Mean:   ", singleGenreRandomScores.mean()
	print "Std dev:", singleGenreRandomScores.std()
	
if __name__ == "__main__":
	main()