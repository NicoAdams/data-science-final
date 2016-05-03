#!/usr/bin/env python
import sys
import json
import porter_stemmer
import re
import string
import operator
import csv

titles_path = ''
lyrics_path = ''
stopwords_path = ''
affinity_path = ''

def main():

    # Store titles and lyrics in dictionary
    with open(titles_path) as titles_f:
        titles = json.load(titles_f)
    with open(lyrics_path) as lyrics_f:
        lyrics = json.load(lyrics_f)

    # Crete dictionary from affinity file
    global affin_dict
    affin_dict = create_affin_dict()

    # sentiments dictionaries with key = spotify id, value = sentiment
    # lyric_sentiments = {}
    # title_sentiments = {}

    # if the song has no lyrics, take them out
    lyrics_dict = {}
    titles_dict = {}
    for item in lyrics:
        if lyrics[item] != '':
            lyrics_dict[item] = lyrics[item]
            titles_dict[item] = titles[item]

    lyric_sentiment = find_lyric_sentiment(lyrics_dict)
    title_sentiment = find_title_sentiment(titles_dict)
    # print lyric_sentiment
    # print title_sentiment
    # sort_dict_sent(lyric_sentiment)
    # sort_dict_sent(title_sentiment)

    with open('lyric_sentiment.txt', 'w') as lyric_out:
        json.dump(lyric_sentiment, lyric_out)
    with open('title_sentiment.txt', 'w') as title_out:
        json.dump(title_sentiment, title_out)



    # name_dict = {}
    # with open(furniture_names_path) as f:
    #     names = list(f.read().splitlines())
    #     for name in names:
    #         name_dict[name] = re.compile(r'\b({0})\b'.format(name), flags=re.IGNORECASE|re.UNICODE)
    #     furn_note_d = furniture_popularity(data, name_dict)
    #     website_popularity(data)
    #     find_sentiment(data, name_dict, furn_note_d)
    # text.translate(dict.fromkeys(ord(c) for c in string.punctuation))

def find_title_sentiment(words_dictionary):
    table = string.maketrans("", "")
    sentiment_dictionary = {}
    # print words_dictionary
    for song in words_dictionary:
        # print song
        # print words_dictionary[song][u'title']


        words = words_dictionary[song][u'title']
        lower_words = words.lower()
        no_stop = filter_out_stopwords(lower_words)
        # no_punc = no_stop.translate(dict.fromkeys(ord(c) for c in string.punctuation))
        stemmed_note = stem_sentence(no_stop)
        # print stemmed_note
        # print words_dictionary[song]
        sentiment_found = calc_string_sent(stemmed_note)
        sentiment_dictionary[song] = sentiment_found
    return sentiment_dictionary

def find_lyric_sentiment(words_dictionary):
    table = string.maketrans("", "")
    sentiment_dictionary = {}
    # print words_dictionary
    for song in words_dictionary:
        # print song
        # print words_dictionary[song]


        words = words_dictionary[song]
        lower_words = words.lower()
        no_stop = filter_out_stopwords(lower_words)
        # no_punc = no_stop.translate(dict.fromkeys(ord(c) for c in string.punctuation))
        stemmed_note = stem_sentence(no_stop)
        # print stemmed_note
        # print words_dictionary[song]
        sentiment_found = calc_string_sent(stemmed_note)
        sentiment_dictionary[song] = sentiment_found
    return sentiment_dictionary


    # table = string.maketrans("", "")
    # sentiments_final = {}
    # for item in furniture_notes:
    #     sum_of_note_sents = 0
    #     total_notes = 0
    #     sentiments_final[item] = 0
    #     for note in furniture_notes[item]:
    #         lower_note = note.lower()
    #         no_stopwords = filter_out_stopwords(lower_note)
    #         no_punc = no_stopwords.translate(table, string.punctuation)
    #         stemmed_note = stem_sentence(no_punc)
    #         indiv_note_sent = calc_string_sent(stemmed_note)  #sentiment for the note we are looking at
    #         sum_of_note_sents = sum_of_note_sents + indiv_note_sent #add the invidual note sentiments together
    #         total_notes = total_notes + 1 #increment the number of notes about the item
    #     if total_notes == 0:
    #         total_notes = 1
    #     item_sent = sum_of_note_sents/total_notes
    #     sentiments_final[item] = item_sent
    # sort_dict_sent(sentiments_final)

def calc_string_sent(s):
    word_count = 0
    sent_sum = 0.0
    for item in s:
        word_count = word_count + 1
        if item in affin_dict:
            sent_sum = float(sent_sum) + float(affin_dict[item])
    if word_count == 0:
        word_count = 1
    return float(float(sent_sum)/float(word_count))

def filter_out_stopwords(s):
    new_s = ""
    with open(stopwords_path, 'r') as f:
        stops = list(f.read().splitlines())
    for word in s.split():
        if word in stops:
            word = ""
        else:
            new_s = new_s + " " + word
    return new_s

# def furniture_popularity(pins, reg_names):
#     '''
#     Input:
#         pins : JSON object of Pinterest pins
#     '''
#     with open(furniture_names_path) as f:
#         popularity = {}
#         furn_note = {}
#         for pin in pins:
#             note = pin['note'].encode('utf-8')
#             for item in reg_names:
#                 if reg_names[item].search(note):
#                     if (popularity.has_key(item)):
#                         popularity[item] = popularity[item] + 1
#                         furn_note[item].append(note)
#                     else:
#                         popularity[item] = 1
#                         furn_note[item] = []
#                         furn_note[item].append(note)

#     sort_dict(popularity)
#     return furn_note

# def sort_dict(dictionary):
#     some_list = dictionary.items()
#     item_list1 = sorted(some_list, key=lambda row: row[0])
#     item_list1.reverse()
#     item_list = sorted(item_list1, key=lambda row: row[1])
#     item_list.reverse()
#     for x in range(0,10):
#         print str(item_list[x][0]) + ", " + str(item_list[x][1])

def sort_dict_sent(dictionary):
    some_list = dictionary.items()
    item_list1 = sorted(some_list, key=lambda row: row[0])
    item_list1.reverse()
    item_list = sorted(item_list1, key=lambda row: row[1])
    item_list.reverse()
    mylen = len(item_list)
    print mylen
    for x in range(0,10):
        print str(item_list[x][0]) + ", " + str(item_list[x][1])
    ii = 10
    for x in range(0,10):
        print str(item_list[mylen-ii][0]) + ", " + str(item_list[mylen-ii][1])
        ii = ii - 1

# def website_popularity(pins):
#     '''
#     Input:
#         pins : JSON object of Pinterest pins
#     '''
#     url_pop = {}
#     for pin in pins:
#         my_pin = pin['original_link']
#         p = re.compile(r'https?:\/\/[^\/]+\/?', flags=re.IGNORECASE).findall(my_pin)
#         for item in p:
#             new_item = item[0:-1]
#             if url_pop.get(new_item, 0) == 0:
#                 url_pop[new_item] = 1
#             else:
#                 url_pop[new_item] = 1 + url_pop[new_item]
#     sort_dict(url_pop)

def create_affin_dict():
    my_dict = {}
    csv_reader = csv.reader(open(affinity_path, 'rb'), delimiter='\t')
    for item in csv_reader:
        my_dict[item[0]] = item[1]
    return my_dict

def stem_sentence(sentence):
    '''
    Stems an entire sentence using Porter Stemming.
    A PorterStemmer is created for you.
    Input:
        sentence (string): A sentence in which each word will be stemmed.
    Output:
        (string): The stemmed form of the input sentence.
    '''
    # Static function stemmer variable
    if 'stemmer' not in stem_sentence.__dict__:
        stem_sentence.stemmer = porter_stemmer.PorterStemmer()
    # Split input sentence on whitespace to stem each word.
    l = sentence.split()
    # Iterate over list of words and stem each one
    for i in range(len(l)):
        l[i] = stem_sentence.stemmer.stem(l[i], 0, len(l[i]) - 1)
    return l

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print 'Usage: python process.py titles lyrics stopwords affinity'
    titles_path = sys.argv[1]
    lyrics_path = sys.argv[2]
    stopwords_path = sys.argv[3]
    affinity_path = sys.argv[4]
    main()
