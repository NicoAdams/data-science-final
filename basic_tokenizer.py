from porter_stemmer import PorterStemmer
import re

# Strips words of non alphanumeric characters. Accounts for non-English character sets
def stripPunctuation(word): return filter(lambda c: c.isalnum(), word)

# -- Tokenizer class --

class Tokenizer(object):
    def __init__(self, stem=False):
        self.stemmer = PorterStemmer()
        self.stem = stem
        self.stopwords = set()
        
        # Ignores empty strings
        self.stopwords.add("")
        
    def addStopwords(self, stopwords):
        # Adds a stopwords list to the tokenization algorithm
        self.stopwords = self.stopwords.union(stopwords)
    
    def stemWord(self, word):
        # Stems word if stemming is on, else does nothing
        if not self.stem:
            return word
        return self.stemmer.stem(word, 0,len(word)-1)
    
    def processWord(self, word):
        word = word.lower()
        
        # Replaces remaining punctuation
        word = stripPunctuation(word)
        
        # Stems word if stemming is enabled
        word = self.stemWord(word)
        
        # Filters numbers
        word = ("" if word.isdigit() else word)
        
        return word
    
    def processLyrics(self, lyrics):
        # Processes words
        
        # -- Splitting --
        lyrics.replace("\n", " ")
        words = lyrics.split()
        
        # -- Processing --
        words = map(self.processWord, words)
        
        # -- Filtering --
        words = filter(lambda w: w not in self.stopwords, words)
        
        # Returns the edited lyrics
        return words
    
    def __call__(self, lyrics):
        # Returns the features of the lyrics
        return self.processLyrics(lyrics)
