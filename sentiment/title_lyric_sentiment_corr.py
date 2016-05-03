#!/usr/bin/env python
import sys
import json
import string
from scipy.stats.stats import pearsonr
import numpy as np   
import matplotlib.pyplot as plt



title_sentiment_path = ''
lyric_sentiment_path = ''

def main():

    # Store titles and lyrics in dictionary
    with open(title_sentiment_path) as titles_f:
        titles = json.load(titles_f)
    with open(lyric_sentiment_path) as lyrics_f:
        lyrics = json.load(lyrics_f)
    title_sent_array = []
    lyric_sent_array = []
    title_sent_with_vals = []
    lyric_sent_with_vals = []
    for item in titles:
        title_sent_array.append(titles[item])
        lyric_sent_array.append(lyrics[item])
        if titles[item] != 0.0:
            title_sent_with_vals.append(titles[item])
            lyric_sent_with_vals.append(lyrics[item])
    print pearsonr(title_sent_array, lyric_sent_array)
    print pearsonr(title_sent_with_vals, lyric_sent_with_vals)
    print np.corrcoef(title_sent_array, lyric_sent_array)
    print np.corrcoef(title_sent_with_vals, lyric_sent_with_vals)
    plt.scatter(title_sent_array, lyric_sent_array)
    plt.show()





if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: python process.py title_sentiment lyric_sentiment'
    title_sentiment_path = sys.argv[1]
    lyric_sentiment_path = sys.argv[2]
    main()
