# Performs K nearest neighbors classification on the lyrics dataset

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import MultiLabelBinarizer
import json
import argparse
import random
from sklearn.cluster import KMeans
import numpy as np
from sklearn import metrics

from basic_tokenizer import Tokenizer

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
	
def vectorizeLabels(genres):
	return MultiLabelBinarizer().fit_transform(genres)

def parseArgs():
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', default="../data/lyrics.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	parser.add_argument('-v', default=False, help='print prog during k-means alg')
	return parser.parse_args()

def main():
	args = parseArgs()
	
	# Labels = first listed genres
	lyricsFile = args.l
	genresFile = args.g
		
	# Loads the files
	lyrics = json.load(open(lyricsFile))
	genres = json.load(open(genresFile))
	
	# Filters empty lyric strings and genre lists
	lyrics = {k: lyrics[k] for k in lyrics if len(lyrics[k])!=0}
	genres = {k: genres[k] for k in genres if len(genres[k])!=0}
	
	# Returns two lists of corresponding lyric-genre pairs
	(lyrics, genres) = joinDicts(lyrics, genres)
	numSongs = len(lyrics)
	
	# Extracts features (lyrics) 
	t = Tokenizer()
	features = extractFeatures(lyrics, t)
	
	# Extracts labels
	singleLabels = map(lambda g: g[0], genres)
	
	# Calculate k-means
	labelCount = np.unique(singleLabels).shape[0]
	km = KMeans(n_clusters=labelCount, init='k-means++', max_iter=100, n_init=1, verbose=args.v)
	km.fit(features)

	# Prints statistics

	print("Homogeneity: %0.3f" % metrics.homogeneity_score(singleLabels, km.labels_))
	print("Completeness: %0.3f" % metrics.completeness_score(singleLabels, km.labels_))
	print("V-measure: %0.3f" % metrics.v_measure_score(singleLabels, km.labels_))
	print("Adjusted Rand-Index: %.3f"
	      % metrics.adjusted_rand_score(singleLabels, km.labels_))
	print("Silhouette Coefficient: %0.3f"
	      % metrics.silhouette_score(features, km.labels_, sample_size=1000))
	
	
if __name__ == "__main__":
	main()