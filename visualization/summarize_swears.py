

##*******************
##The way that this code was used was that it was added to/the outputs were commented out/overwritten after it 
##was run and the speciic run's output was made into a saved file, so you will find code/variables not used
##in the specific iteration submitted here
##*******************

# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import json
import csv
import argparse
import random
from basic_tokenizer import Tokenizer
from util import levenshtein


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-info', default="./swear_info.txt", help='Path to song summary file')
    parser.add_argument('-results', default="./swear_summary.txt", help='Path to results file')
    parser.add_argument('-max', default=2, help='Maximum levenshtein distance')
    return parser.parse_args()

#makes it so that words that actually mean (eg fucking/fuckin) the same thing are counted as the same word
def synonym(swear):
    if swear in ["motherfucker", "motherfuckers", "motherfucking"]:
        return "motherfucker"
    if swear in ["fuck", "fucking", "fucked", "fuckin"]:
        return "fuck"
    if swear in ["bitch", "bitches"]:
        return "motherfucker"

    #these words are commented out in the html vizualization it is important to know that they are in the songs, 
    #but we decided we would rather not talk about them at the poster fair 
    if swear in ["niggaz", "nigga", "niggas"]:
        return "nigga"

    #if it is not a synonym then it just returns the original word
    return swear


#does all the counting etc -- more info below
def main():
    args = parseArgs()

    songInfo = json.load(open(args.info))

    summary = { }
    allSwears = []
    for songId in songInfo:
        song = songInfo[songId]

        year = song["year"].encode('utf-8')
        # If it's seen the year associated with a song before, just add all the info to that year, otherwise it creates a new year and adds all the info to that
        try:
            yearInfo = summary[year]
        except Exception as e:
            yearInfo = { "swear-words" : [], "word-count" : 0, "genres" : [], "frequencies" : {} }
            summary[year] = yearInfo

        ##print song
        for swear in song["swear-words"]:
            # looks through all the synonyms first
            swear = synonym(swear)
            if swear not in allSwears:
                # Makes a list of the swear words that actually do appear in any of our data
                allSwears.append(swear.encode('utf-8'))
            yearInfo["swear-words"].append(swear.encode('utf-8'))

            try:
                yearInfo["frequencies"][swear] += 1
            except Exception as e:
                yearInfo["frequencies"][swear] = 1

            #this was because there was an odd spike in this year (with the word lust), so I was trying to figure out what it was
            if year == "1963":
                print swear

        #makes a list of the genres encountered in the songs
        for genre in song["genres"]:
            if genre not in yearInfo["genres"]:
                yearInfo["genres"].append(genre)

        yearInfo["word-count"] += song["word-count"]

    totals = ['totals']
    years = []
    uniques = ['uniques']
    frequencies = {}

    swearsByYear = { }
    for swear in allSwears:
        swearsByYear[swear] = [swear]

    for year in sorted(summary):
        yearInfo = summary[year]
        totalSwears = len(yearInfo["swear-words"])
        uniqueSwears = len(set(yearInfo["swear-words"]))
        lyricCount = yearInfo["word-count"]
        years.append(year.encode('utf-8'))
        totals.append(totalSwears)
        uniques.append(uniqueSwears)

        for swear in allSwears:
            if swear in yearInfo["frequencies"]:
                swearCount = yearInfo["frequencies"][swear]
                swearsByYear[swear].append(swearCount/float(yearInfo["word-count"]))
            else:
                swearsByYear[swear].append(0)

        '''
        print "\n" + str(year) + ": "
        print "  ratio = " + "{0:.2f}".format(100 * totalSwears / float(lyricCount))
        print "  total swear count = " + str(totalSwears)
        print "  unique swear count = " + str(uniqueSwears)
        print "  word count = " + str(lyricCount)
        print "  genre count = " + str(len(yearInfo["genres"]))
        print "  genres = " + str(yearInfo["genres"])
        '''

    # does exactly what it says, it sums the swears it encounters, and gives them labels -- sets up the array
    sumsOfSwears = {swear : 0 for swear in allSwears }
    for swear in swearsByYear:
        #I really want the swears by which they happen in 
        sumsOfSwears[swear] += sum(swearsByYear[swear][1:])

    counter = 0
    # It prints them out in order of the most used swear to the least used, so I can viz only the swears that show up the most frequently 
    # ie the ones that are interesting to look at
    for swear in sorted(sumsOfSwears, key=sumsOfSwears.get, reverse=True):
        #print swear + ": " + str(sumsOfSwears[swear])
        print str(swearsByYear[swear]) + ","
        counter += 1
        if counter > 20:
            break

    print allSwears
    print str(totals) + " swear words total"
    print str(len(songInfo) + " songs analyzed"
    '''
    print years
    print uniques
    '''

    if len(summary) > 0:
        with open(args.results, "w") as f:
            json.dump(summary, f)

    
if __name__ == "__main__":
    main()