from sklearn.feature_extraction.text import CountVectorizer
import csv
import re
import random

class FeatureExtractor(object):
    def __init__(self, tokenizer, stopwordsfilename=None, sentimentfilename=None, randomizeSentiments=False):
        self.set_tokenizer(tokenizer)
        self.set_stopwords(stopwordsfilename)
        self.set_sentiment(sentimentfilename, randomizeSentiments=randomizeSentiments)
        self.__r = re.compile(r'\W+')

    def set_tokenizer(self, tokenizer):
        self.__tokenizer = tokenizer

    def set_stopwords(self, stopwordsfilename):
        if stopwordsfilename is not None:
            with open(stopwordsfilename, 'r') as f:
                self.__stopwords = [word.lower().strip() for word in f]
        else:
            self.__stopwords = None
    
    def __shuffle_sentiment(self):
        words = self.__sentiments.keys()
        randWords = list(words)
        random.shuffle(randWords)
        self.__sentiments = {randWords[i]: self.__sentiments[words[i]] for i in xrange(len(words))}    
    
    def set_sentiment(self, sentimentfilename, randomizeSentiments=False):
        if sentimentfilename is not None:
            with open(sentimentfilename, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                self.__sentiments = {word.lower(): int(sentiment) for word, sentiment in reader}
                
                # Randomizes the sentiment associations
                if randomizeSentiments:
                    self.__shuffle_sentiment()
        else:
            self.__sentiments = None

    def __filter_stopwords(self, words):
        return [word.lower() for word in words if word.lower() not in self.__stopwords] if self.__stopwords else words

    def __split(self, inputStr):
        words = self.__filter_stopwords(self.__r.split(inputStr))
        return [word for word in words if word != '']

    def __get_sentiment(self, word):
        return self.__sentiments[word] if word in self.__sentiments else 0.

    def __count_words(self, words):
        word_count_pairs = {}
        for word in words:
            if word in word_count_pairs:
                word_count_pairs[word] += 1
            else:
                word_count_pairs[word] = 1
        return word_count_pairs.items()

    def __sort_by_sent(self, inputStr, binary, reverse=False):
        words = self.__split(inputStr)
        if binary:
            word_sent_pairs = [(word, self.__get_sentiment(word)) for word in set(words)]
            sorted_words = sorted(word_sent_pairs, key=lambda (item, sent): sent, reverse=True)
        else:
            word_sent_pairs = [((word, count), self.__get_sentiment(word)) for word, count in self.__count_words(words)]
            sorted_words = sorted(word_sent_pairs, key=lambda (item, sent): sent, reverse=True)
        return self.__remove_sent(sorted_words)

    def __remove_sent(self, word_sent_pairs):
        return [word for word, sent in word_sent_pairs]

    def __repeat_words(self, word_count_pairs):
        unflattened_list = [[word for i in range(count)] for word, count in word_count_pairs]
        return [word for sublist in unflattened_list for word in sublist]

    def extract_all(self, inputStr, binary=True):
        '''
        Makes a feature vector using all words from the given string.
        :param inputStr: an input string
        :param binary: option to make binary feature vector (True) or count feature vector (False)
        :return: Feature vector made from all words in the input
        '''
        return inputStr

    def extract_top_n(self, inputStr, n, binary=True):
        '''
        Makes a feature vector using the top n sentiment words from the given string.
        :param input: an input string
        :param n: the number of top words to keep
        :param binary: option to make a binary feature vector (True) or count feature vector (False)
        :return: Feature vector made from the top n words in the input
        '''
        assert self.__sentiments is not None
        assert n >= 1

        sorted_words = self.__sort_by_sent(inputStr, binary, reverse=True)
        if len(sorted_words) >= n:
            words = sorted_words[:n] if binary else self.__repeat_words(sorted_words[:n])
        else:
            words = sorted_words if binary else self.__repeat_words(sorted_words)
        return self.extract_all(" ".join(words), binary=binary)

    def extract_bottom_n(self, inputStr, n, binary=True):
        '''
        Makes a feature vector using the bottom n sentiment words from the given string
        :param inputStr: an input string
        :param n: the number of top words to keep
        :param binary: option to make a binary feature vector (True) or count feature vector (False)
        :return: feature vector made from the bottom n words in the input
        '''
        assert self.__sentiments is not None
        assert n >= 1

        sorted_words = self.__sort_by_sent(inputStr, binary, reverse=False)
        if len(sorted_words) >= n:
            words = sorted_words[:n] if binary else self.__repeat_words(sorted_words[:n])
        else:
            words = sorted_words if binary else self.__repeat_words(sorted_words)
        return self.extract_all(" ".join(words), binary=binary)

    def extract_top_n_bottom_m(self, inputStr, n, m, binary=True):
        '''
        Makes a feature vector using the top n and bottom m words from the given string
        :param inputStr: an input string
        :param n: the number of top words to keep
        :param m: the number of bottom words to keep
        :param binary: option to make a binary feature vector (True) or count feature vector (False)
        :return: feature vector made from the top n and bottom m words in the input
        '''

        assert self.__sentiments is not None
        assert n >= 1
        assert m >= 1
        sorted_words = self.__sort_by_sent(inputStr, binary, reverse=True)
        if len(sorted_words) >= n + m:
            top_words = sorted_words[:n] if binary else self.__repeat_words(sorted_words[:n])
            bottom_words = sorted_words[-m:] if binary else self.__repeat_words(sorted_words[-m:])
            words = top_words + bottom_words
        else:
            words = sorted_words if binary else self.__repeat_words(sorted_words)
        return self.extract_all(" ".join(words), binary=binary)

if __name__ == "__main__":
    from basic_tokenizer import Tokenizer

    tokenizer = Tokenizer()
    stopwordsfilename = "C:/Users/Alex/Documents/Brown/Spring 2016/CSCI1951A/final/data-science-final/util_data/stopwords.txt"
    sentimentfilename = "C:/Users/Alex/Documents/Brown/Spring 2016/CSCI1951A/assignments/integration/data/AFINN-111.tsv"
    extractor = FeatureExtractor(tokenizer, stopwordsfilename=stopwordsfilename, sentimentfilename=sentimentfilename)
    songs = ["Happy happy joy joy happy happy joy joy happy happy joy joy happy happy joy joy happy happy joy joy happy happy joy joy happy happy joy joy joy"]
    for song in songs:
        extractor.extract_top_n(song, 3, binary=False)