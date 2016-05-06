#!/usr/bin/env python
import sys
import json
import porter_stemmer
import re
import string
import operator
import csv
import numpy as np
import matplotlib.pyplot as plt

titles_path = ''
lyrics_path = ''

def main():

    with open(sentiments_path) as sf:
        sents = json.load(sf)
    with open(years_path) as yf:
        years = json.load(yf)

    year_sent_arrays = {}
    for item in years:
        if years[item] != '':
            year_sent_arrays[years[item]] = []

    for item in sents:
        if years[item] != '' and sents[item] != '':
            year_sent_arrays[years[item]].append(sents[item])

    avg_sents = {}

    for year in year_sent_arrays:
        avg_sents[year] = np.mean(year_sent_arrays[year])

    years_plt = []
    sents_plt = []

    for item in sorted(avg_sents):
        years_plt.append(item)
        sents_plt.append(avg_sents[item])

    plt.plot(years_plt, sents_plt)
    plt.show()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print len(sys.argv)
        print 'Usage: python year_sent.py sentiment years'
    else:
        sentiments_path = sys.argv[1]
        years_path = sys.argv[2]
        main()
