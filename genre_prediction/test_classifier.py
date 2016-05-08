# Tests a classifier on the dataset using cross-validation

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from sklearn import cross_validation
from basic_tokenizer import Tokenizer

# Mutlilabel classification
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
import random

def testSingle(classifier, features, singleLabels, randSentimentFeatures=None):
	# Tests the classifier on the top-genre classification problem
	
	# Shuffles the labels to randomize them
	randomSingleLabels = list(singleLabels)
	random.shuffle(randomSingleLabels)
	
	crossVal = 5 # Number of folds
		
	# Cross-validation: Standard model
	singleGenreScores = cross_validation.cross_val_score( \
		classifier, features, singleLabels, cv=crossVal, scoring='accuracy' \
	)
	print "-- Single-genre model --"
	print "Mean:   ", singleGenreScores.mean()
	print "Std dev:", singleGenreScores.std()
	
	# Cross-validation: Random labels
	singleRandomGenreScores = cross_validation.cross_val_score( \
		classifier, features, randomSingleLabels, cv=crossVal, scoring='accuracy' \
	)
	print "-- Random genre model --"
	print "Mean:   ", singleRandomGenreScores.mean()
	print "Std dev:", singleRandomGenreScores.std()
	
	if randSentimentFeatures is not None:
		# Cross-validation: Random sentiments
		singleGenreRandomSentimentScores = cross_validation.cross_val_score( \
			classifier, randSentimentFeatures, singleLabels, cv=crossVal, scoring='accuracy' \
		)
		print "-- Single-genre model (random sentiments) --"
		print "Mean:   ", singleGenreRandomSentimentScores.mean()
		print "Std dev:", singleGenreRandomSentimentScores.std()
	
def testMulti(classifier, features, labels):
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
	print "-- Multi-genre model --"
	print "Mean:   ", multiGenreScores.mean()
	print "Std dev:", multiGenreScores.std()
	
	# Cross-validation: Random single labels
	multiGenreRandomScores = cross_validation.cross_val_score( \
		OneVsRestClassifier(classifier), features, randomMultiLabels, cv=crossVal, scoring='accuracy' \
	)
	print "-- Random multi-genre model --"
	print "Mean:   ", multiGenreRandomScores.mean()
	print "Std dev:", multiGenreRandomScores.std()	
