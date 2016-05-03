# Performs K nearest neighbors classification on the lyrics dataset

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from sklearn.neighbors import KNeighborsClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import cross_validation
import json
import argparse
from basic_tokenizer import Tokenizer


def getJSON(filename):
	json

def joinDicts(d1, d2):
	# Inner joins two dicts on their keys
	join = ([],[])
	for k in d1:
		if k in d2:
			join[0].append(d1[k])
			join[1].append(d2[k])
	return join

def extractFeatures(lyrics, tokenizer):
	v = CountVectorizer(binary=True, lowercase=True, tokenizer=tokenizer)
	return v.fit_transform(lyrics)
	

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', default=5, help='Number of neighbors to train the classifier on')
	parser.add_argument('-l', default="../data/lyrics.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	parser.add_argument('-c', default=5, help='Number of folds in the cross-validation')
	return parser.parse_args()

def main():
	args = parseArgs()
	
	# Labels = first listed genres
	lyricsFile = args.l
	genresFile = args.g
	
	try:
		n = int(args.n)
		c = int(args.c)
	except ValueError:
		print e
		return
	
	# Loads the files
	lyrics = json.load(open(lyricsFile))
	genres = json.load(open(genresFile))
	
	# Filters empty genre lists
	genres = {k: genres[k] for k in genres if len(genres[k])!=0}
	
	# Returns two lists of corresponding lyric-genre pairs
	(lyrics, genres) = joinDicts(lyrics, genres)
	numSongs = len(lyrics)
	
	# Extracts features (lyrics) 
	t = Tokenizer()
	features = extractFeatures(lyrics, t)
	
	# Extracts labels (the first genre in each list)
	labels = map(lambda g: g[0], genres)
	
	# Trains the classifier
	knn = KNeighborsClassifier(neighbors=n)
	
	# Cross-validation
	scores = cross_validation.cross_val_score( \
		knn, features, labels, cv=c, scoring='accuracy' \
	)
	
	# Prints statistics
	print "Mean:", scores.mean()
	print "Std dev:", scores.std() 
	
if __name__ == "__main__":
	main()