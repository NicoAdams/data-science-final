# Tests classifiers on their general performance

import test_classifier
import argparse

# ML algorithms
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import BernoulliRBM
from sklearn.svm import LinearSVC

def parseArgs():
	parser = argparse.ArgumentParser()
	
	# Files
	parser.add_argument('-l', default="../data/lyrics.txt", help='Path to lyrics data')
	parser.add_argument('-g', default="../data/genres.txt", help='Path to the genres data')
	parser.add_argument('-s', default="../util_data/stopwords.txt", help='Path to stopwords file')
	
	# Conditions
	parser.add_argument('-c', required=True, help='Classifier type: nb, knn, rbm, svm')
	parser.add_argument('--stem', action="store_true", help='Stem words')
	parser.add_argument('--sw', action="store_true", help='Leave stopwords in')
	parser.add_argument('--count', action="store_true", help='Use counts instead of binary features')
	return parser.parse_args()

def main():
	args = parseArgs()
	
	# Conditions
	stemWords = args.stem
	removeStopwords = not args.sw
	binary = not args.count
	
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
	
	# Tests the classifier
	test_classifier.test(classifier, \
		stemWords=stemWords, removeStopwords=removeStopwords, binary=binary)

if __name__=="__main__":
	main()