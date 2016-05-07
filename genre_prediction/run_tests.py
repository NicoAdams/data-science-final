# Tests classifiers on their general performance

import test_classifier
import argparse

# ML algorithms
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import BernoulliRBM
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

def parseArgs():
	parser = argparse.ArgumentParser()
	
	# Files
	parser.add_argument('-l', default="../data/lyrics.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	parser.add_argument('-s', default="../util_data/stopwords.txt", help='Path to stopwords file')
	parser.add_argument('-a', default="../util_data/AFINN-111.tsv", help='Path to stopwords file')
	
	# Conditions
	parser.add_argument('-c', required=True, help='Classifier type: nb, knn, rbm, svm')
	parser.add_argument('--stem', action="store_true", help='Stem words')
	parser.add_argument('--sw', action="store_true", help='Leave stopwords in')
	parser.add_argument('--count', action="store_true", help='Use counts instead of binary features')
	parser.add_argument('--multi', action="store_true", help='Trains one classifier per genre')
	parser.add_argument('--top', type=int, default=0, help='Number of top-sentiment words to use')
	parser.add_argument('--bottom', type=int, default=0, help='Number of bottomw-sentiment words to use')
	return parser.parse_args()

def main():
	args = parseArgs()
	
	# Conditions
	stemWords = args.stem
	removeStopwords = not args.sw
	binary = not args.count
	multi = args.multi
	sentimentTop = args.top
	sentimentBottom = args.bottom
	
	# Creates the classifier
	if args.c=='nb':
		classifier = BernoulliNB(binarize=None)
		
	elif args.c=='knn':
		numNeighbors = 10
		classifier = KNeighborsClassifier(n=10)
		
	elif args.c=='rbm':
		classifier = BernoulliRBM()
		
	elif args.c=='svm':
		classifier = LinearSVC()
		
	elif args.c=='rf':
		numTrees = 10
		classifier = RandomForestClassifier(n_estimators=numTrees)
	
	# Tests the classifier
	test_classifier.test(classifier, \
		lyricsFile=args.l, genresFile=args.g, stopwordsFile=args.s, sentimentFile=args.a, \
		stemWords=stemWords, removeStopwords=removeStopwords, binary=binary, multi=multi, \
		sentimentTop=sentimentTop, sentimentBottom=sentimentBottom)

if __name__=="__main__":
	main()