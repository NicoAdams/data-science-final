# Tests a classifier on the dataset using cross-validation

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn import cross_validation
from basic_tokenizer import Tokenizer
import json
import random
import math
import numpy

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

def loadStopwords(filename):
	# Loads the stop words
	stopwords = open(filename).readlines()
	stopwords = map(lambda l: l.strip(), stopwords)
	return stopwords

def test(classifier, \
	lyricsFile='../data/lyrics.txt', genresFile='../data/genres.txt', stopwordsFile='../util_data/stopwords.txt',
	stemWords=True, removeStopwords=True, binary=True):
	
	# Prints the conditions
	
	print "Classifier:", type(classifier)
	conditions = ""
	conditions += ("Stemming, " if stemWords else "No stemming, ")
	conditions += ("binary, " if binary else "count, ")
	conditions += "stopwords "+("removed" if removeStopwords else "included")
	print conditions
	print
	
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
	
	# Shuffles the labels to randomize them
	randomSingleLabels = list(singleLabels)
	random.shuffle(randomSingleLabels)
	
	crossVal = 5 # Number of folds
	
	print
	print "Number of songs:", numSongs
	
	# Cross-validation: Single Labels
	singleGenreScores = cross_validation.cross_val_score( \
		classifier, features, singleLabels, cv=crossVal, scoring='accuracy' \
	)
	print "-- Single-genre model --"
	print "Mean:   ", singleGenreScores.mean()
	print "Std dev:", singleGenreScores.std()
	
	# Cross-validation: Random single labels
	singleGenreRandomScores = cross_validation.cross_val_score( \
		classifier, features, randomSingleLabels, cv=crossVal, scoring='accuracy' \
	)
	# Prints statistics
	print "-- Random genre model --"
	print "Mean:   ", singleGenreRandomScores.mean()
	print "Std dev:", singleGenreRandomScores.std()	
