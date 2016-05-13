
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

def main():
    args = parseArgs()

    songInfo = json.load(open(args.info))

    summary = { }

    totalCurses = {}
    yearCurses ={}

    topCurses = {'fuck':0, 'shit':0, 'lust':0, 'ass':0, 'sex':0, 'bitch':0, 'fucking':0}

    for songId in songInfo:
        song = songInfo[songId]

        year = song["year"]
        try:
            yearInfo = summary[year]
        except Exception as e:
            yearInfo = { "swear-words" : [], "word-count" : 0, "genres" : [], "songs-with-swears" : 0, "song-count" : 0, "top-curses":{'fuck':0, 'shit':0, 'lust':0, 'ass':0, 'sex':0, 'bitch':0, 'fucking':0}}
            summary[year] = yearInfo

        ##print song
        for swear in song["swear-words"]:
            if swear not in totalCurses:
                totalCurses[swear] = 1
            else:
                totalCurses[swear] += 1
            if swear not in yearInfo["swear-words"]:
                yearInfo["swear-words"].append(swear)
                yearCurses[swear] = 1

                # if swear in topCurses:
                #     yearInfo["top-curses"][swear] +=1
            if swear in yearInfo["top-curses"]:
                yearInfo["top-curses"][swear] += 1
            else:
                yearCurses[swear] += 1



        if len(song["swear-words"]) is not 0:
            yearInfo["songs-with-swears"] += 1


        for genre in song["genres"]:
            if genre not in yearInfo["genres"]:
                yearInfo["genres"].append(genre)

        yearInfo["word-count"] += song["word-count"]
        yearInfo["song-count"] += 1

    sortedCurses = sorted(totalCurses.items(), key=lambda (key, value): value)

    for year in sorted(summary):
        yearInfo = summary[year]
        totalSwears = len(yearInfo["swear-words"])
        uniqueSwears = len(set(yearInfo["swear-words"]))
        lyricCount = yearInfo["word-count"]

        swearRatios = {}
        swearRatio = 0
        # print str(year) + "\t" + str(yearInfo["top-curses"])
        for swear in yearInfo["top-curses"]:
            if totalSwears is not 0:
                swearRatio = yearInfo["top-curses"][swear] / float(totalSwears)
                swearRatios[swear] = swearRatio

        print str(year) + "\t" + str(swearRatios)
        # print str(year) + "\t" + str(yearInfo["top-curses"])
    # print sortedCurses

        # print str(year) + "\t" + str(totalSwears / float(lyricCount))

        # print str(year) + "\t" + str(yearInfo["songs-with-swears"] / float(yearInfo["song-count"]))

        # print "\n" + str(year) + ": "
        # print "  ratio = " + "{0:.2f}".format(100 * totalSwears / float(lyricCount))
        # print "  total swear count = " + str(totalSwears)
        # print "  unique swear count = " + str(uniqueSwears)
        # print "  word count = " + str(lyricCount)
        # print "  genre count = " + str(len(yearInfo["genres"]))
        # print "  genres = " + str(yearInfo["genres"])

    if len(summary) > 0:
        with open(args.results, "w") as f:
            json.dump(summary, f)

    
if __name__ == "__main__":
    main()