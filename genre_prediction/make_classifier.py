# Creates classifiers and tests their general performance

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

# ML algorithms
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import BernoulliRBM
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

from sklearn.base import clone
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer

import test_classifier
import argparse
import json
import cPickle as pickle
from basic_tokenizer import Tokenizer
from feature_extractor import FeatureExtractor

def parseArgs():
	parser = argparse.ArgumentParser()
	
	# Files
	parser.add_argument('-l', default="../data/lyrics.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	parser.add_argument('-s', default="../util_data/stopwords.txt", help='Path to stopwords file')
	parser.add_argument('-a', default="../util_data/AFINN-111.tsv", help='Path to stopwords file')
	
	# Actions
	parser.add_argument('--test', action="store_true", default=True, help="Run cross-validation on the classifier")
	
	# Conditions
	parser.add_argument('-c', required=True, help='Classifier type: nb, knn, rbm, svm')
	parser.add_argument('--stem', action="store_true", help='Stem words')
	parser.add_argument('--sw', action="store_true", help='Leave stopwords in')
	parser.add_argument('--count', action="store_true", help='Use counts instead of binary features')
	parser.add_argument('--idf', action="store_true", help='Use tf-idf weighting')
	parser.add_argument('--top', type=int, default=0, help='Number of top-sentiment words to use')
	parser.add_argument('--bottom', type=int, default=0, help='Number of bottomw-sentiment words to use')
	return parser.parse_args()

# -- Functions for loading and processing features --

def loadStopwords(filename):
	# Loads the stop words
	stopwords = open(filename).readlines()
	stopwords = map(lambda l: l.strip(), stopwords)
	return stopwords

def vectorizeFeatures(lyrics, tokenizer, binary=True, idf=False):
	if not idf:
		v = CountVectorizer(binary=binary, lowercase=True, tokenizer=tokenizer)
	else:
		v = TfidfVectorizer(binary=binary, lowercase=True, tokenizer=tokenizer)
	return v.fit_transform(lyrics)

def extractFeatures(lyrics, tokenizer, sentimentFile, \
	binary=True, idf=False, \
	sentimentTop=0, sentimentBottom=0, randomizeSentiments=False):

	fe = FeatureExtractor(tokenizer, sentimentfilename=sentimentFile, randomizeSentiments=randomizeSentiments)
	
	if sentimentTop != 0 and sentimentBottom != 0:
		features = [fe.extract_top_n_bottom_m(l, sentimentTop, sentimentBottom) for l in lyrics]
	elif sentimentTop != 0:
		features = [fe.extract_top_n(l, sentimentTop) for l in lyrics]
	elif sentimentBottom != 0:
		features = [fe.extract_bottom_n(l, sentimentBottom) for l in lyrics]
	else:
		features = lyrics
	
	return vectorizeFeatures(lyrics, tokenizer, binary=binary)

def joinDicts(d1, d2):
	# Inner joins two dicts on their keys
	join = ([],[])
	for k in d1:
		if k in d2:
			join[0].append(d1[k])
			join[1].append(d2[k])
	return join

# -- Creates, tests and saves a classifier --

def main():
	args = parseArgs()
	
	# Files
	lyricsFile = args.l
	genresFile = args.g
	stopwordsFile = args.s
	sentimentsFile = args.a
	
	# Actions
	test = args.test
		
	# Conditions
	stemWords = args.stem
	removeStopwords = not args.sw
	binary = not args.count
	idf = args.idf
	sentimentTop = args.top
	sentimentBottom = args.bottom
	
	
	conditions = ""
	conditions += ("Stemming" if stemWords else "No stemming")
	conditions += ", "
	conditions += ("binary" if binary else "count ")
	conditions += (" IDF" if idf else "")
	conditions += ", "
	conditions += "stopwords "+("removed" if removeStopwords else "included")
	
	# Creates the classifier
	if args.c=='nb':
		classifier = BernoulliNB(binarize=None)
		
	elif args.c=='knn':
		conditions += " (neighbors="+str(numNeighbors)+")"
		numNeighbors = 10
		classifier = KNeighborsClassifier(n=10)
		
	elif args.c=='rbm':
		classifier = BernoulliRBM()
		
	elif args.c=='svm':
		classifier = LinearSVC()
		
	elif args.c=='rf':
		numTrees = 50
		conditions += " (trees="+str(numTrees)+")"
		classifier = RandomForestClassifier(n_estimators=numTrees)
	
	print "Classifier:", type(classifier)
	print conditions
	print
	
	# -- Creates the classifier --
	
	# Loads the data files
	lyrics = json.load(open(lyricsFile))
	genres = json.load(open(genresFile))
	
	# Filters empty lyric strings and genre lists
	lyrics = {k: lyrics[k] for k in lyrics if len(lyrics[k])!=0}
	genres = {k: genres[k] for k in genres if len(genres[k])!=0}
	
	# Returns two lists of corresponding lyric-genre pairs
	(lyrics, genres) = joinDicts(lyrics, genres)
	
	# Creates a tokenizer
	t = Tokenizer(stem=stemWords)
	if removeStopwords:
		t.addStopwords(loadStopwords(stopwordsFile))
	
	# Extracts features
	features = extractFeatures(lyrics, t, sentimentsFile, binary=binary, idf=idf, \
		sentimentTop=sentimentTop, sentimentBottom=sentimentBottom)
	usingSentiment = (sentimentTop != 0 or sentimentBottom != 0)
	
	# Extracts labels
	labels = map(lambda g: g[0], genres)
	
	# Fits the classifier
	classifier.fit(features, labels)
	
	# -- Saves the classifier object to file --
	
	name = ""
	name += args.c+" - "
	name += conditions
	
	# Must be run from within genre/prediction for this step to work
	fname = "classifiers/"+name
	with open(fname, "w+") as f:
		pickle.dump(classifier, f)
	print
	print "Saved the classifier to", fname
	
	# -- Tests the classifier --
	
	if test:
		
		randSentimentFeatures = None
		if usingSentiment:
			randSentimentFeatures = extractFeatures( \
				lyrics, t, sentimentsFile, binary=binary, idf=idf, \
				sentimentTop=sentimentTop, sentimentBottom=sentimentBottom, \
				randomizeSentiments=True)
		
		classifierCopy = clone(classifier)
		test_classifier.testSingle(classifierCopy, \
			features, labels, randSentimentFeatures=randSentimentFeatures)	

if __name__=="__main__":
	main()