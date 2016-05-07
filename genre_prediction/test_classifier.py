# Tests a classifier on the dataset using cross-validation

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn import cross_validation
from basic_tokenizer import Tokenizer
from sklearn.preprocessing import MultiLabelBinarizer
from feature_extractor import FeatureExtractor
import json
import random
import math
import numpy
import csv

def joinDicts(d1, d2):
	# Inner joins two dicts on their keys
	join = ([],[])
	for k in d1:
		if k in d2:
			join[0].append(d1[k])
			join[1].append(d2[k])
	return join

def vectorizeFeatures(lyrics, tokenizer, binary=True):
	v = CountVectorizer(binary=binary, lowercase=True, tokenizer=tokenizer)
	return v.fit_transform(lyrics)

def loadStopwords(filename):
	# Loads the stop words
	stopwords = open(filename).readlines()
	stopwords = map(lambda l: l.strip(), stopwords)
	return stopwords

def vectorizeLabels(genres):
	# Returns a vectorized representation of genre labels. Use when building multi-label models
	return MultiLabelBinarizer().fit_transform(genres)

def testSingle(classifier, features, genres):
	# Tests the classifier on the top-genre classification problem
	
	# Extracts labels
	singleLabels = map(lambda g: g[0], genres)
	
	# Shuffles the labels to randomize them
	randomSingleLabels = list(singleLabels)
	random.shuffle(randomSingleLabels)
	
	crossVal = 5 # Number of folds
		
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

def testMulti(classifier, features, genres):
	# Tests the classifier on a one-vs-all model.
	
	# Extracts labels
	multiLabels = vectorizeLabels(genres)
	
	# Shuffles the labels to randomize them
	randomMultiLabels = list(multiLabels)
	random.shuffle(randomMultiLabels)
	
	crossVal = 5 # Number of folds
	
	# Cross-validation: Single Labels
	multiGenreScores = cross_validation.cross_val_score( \
		OneVsRestClassifier(classifier), features, multiLabels, cv=crossVal, scoring='accuracy' \
	)
	print "-- Mutli-genre model --"
	print "Mean:   ", multiGenreScores.mean()
	print "Std dev:", multiGenreScores.std()
	
	# Cross-validation: Random single labels
	multiGenreRandomScores = cross_validation.cross_val_score( \
		OneVsRestClassifier(classifier), features, randomMultiLabels, cv=crossVal, scoring='accuracy' \
	)
	print "-- Random multi-genre model --"
	print "Mean:   ", multiGenreRandomScores.mean()
	print "Std dev:", multiGenreRandomScores.std()	


def test(classifier, \
	lyricsFile='../data/lyrics.txt', genresFile='../data/genres.txt', stopwordsFile='../util_data/stopwords.txt', sentimentFile='../util_data/AFINN-111.tsv', \
	stemWords=True, removeStopwords=True, binary=True, multi=False, sentimentTop=0, sentimentBottom=0):
	
	# Prints the conditions
	
	print "Classifier:", type(classifier)
	conditions = ""
	conditions += ("Stemming, " if stemWords else "No stemming, ")
	conditions += ("binary, " if binary else "count, ")
	conditions += "stopwords "+("removed" if removeStopwords else "included")
	print conditions
	if multi: print "Multi-genre model"
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
	
	# Creates a tokenizer and feature extractor
	
	t = Tokenizer(stem=stemWords)
	if removeStopwords:
		t.addStopwords(loadStopwords(stopwordsFile))
	
	fe = FeatureExtractor(t, sentimentfilename=sentimentFile)
	if sentimentTop != 0 and sentimentBottom != 0:
		features = [fe.extract_top_n_bottom_m(l, sentimentTop, sentimentBottom) for l in lyrics]
	elif sentimentTop != 0:
		features = [fe.extract_top_n(l, sentimentTop) for l in lyrics]
	elif sentimentBottom != 0:
		features = [fe.extract_bottom_n(l, sentimentBottom) for l in lyrics]
	else:
		features = lyrics
	
	# Vectorizes the features
	features = vectorizeFeatures(features, t, binary=binary)
	
	# Processes features with respect to sentiment
	
	print
	print "Number of songs:", numSongs

	# Tests the classifier against top genres only
	if not multi:
		testSingle(classifier, features, genres)
	else:
		testMulti(classifier, features, genres)
