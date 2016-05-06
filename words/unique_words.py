#!/usr/bin/env python
import sys
import json

lyrics_path = ''

def main():

    with open(lyrics_path) as lf:
        lyrics = json.load(lf)


    uniq_words = {}
    total_words = {}
    uniq_ratio = {}
    for song in lyrics:
        if lyrics[song] != '':
            words = []
            total_word_count = 0
            for word in lyrics[song].split():
                total_word_count += 1
                if word not in words:
                    words.append(word)
            uniq_words[song] = len(words)
            total_words[song] = total_word_count
            uniq_ratio[song] = float(float(len(words))/float(total_word_count))

    

    with open('unique_words.txt', 'w') as uf:
        json.dump(uniq_words, uf)
    with open('total_words.txt', 'w') as tf:
        json.dump(total_words, tf)
    with open('unique_words_ratio.txt', 'w') as rf:
        json.dump(uniq_ratio, rf)



if __name__ == '__main__':
    if len(sys.argv) < 2:
        print len(sys.argv)
        print 'Usage: python unique_words.py lyrics_path'
    else:
        lyrics_path = sys.argv[1]
        main()
