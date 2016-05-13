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
    parser.add_argument('-stop', default="../util_data/stopwords.txt", help='Path to stop words')
    parser.add_argument('-lyrics', default="../data/lyrics.txt", help='Path to lyrics data')
    parser.add_argument('-results', default="./swear_info.txt", help='Path to results file')
    parser.add_argument('-genres', default="../data/genres.txt", help='Path to the genres data')
    parser.add_argument('-csv', default="../data/datascience.csv", help='Path to the song data')
    parser.add_argument('-years', default="../discogs/year_data.json", help='Path to the song year data')
    parser.add_argument('-swears', default="../data/swear-words.csv", help='Path to swear words')
    parser.add_argument('-max', default=2, help='Maximum levenshtein distance')
    return parser.parse_args()

def makeSong(title, artist, album, genres, duration, year):
    return {"title": title, "artist": artist, "album": album, "genres": genres, "duration": duration, "year": year}

# Dont want to pay attention to stop words when looking at word count etc. 
def stripStopWords(string, stopwords):
    result = []
    for word in string.split():
        if len(word) == 0:
            continue;
        word = word.encode('utf-8').lower()
        if word not in stopwords:
            result.append(word)

    return result

# Build of dictionary by combining the information in the song list scraped from Spotify with the
# genre information from LastFM and the album release year from discogs.
def generateSongInfo(csvFile, genresFile, yearsFile):
    genres = json.load(open(genresFile))
    years = json.load(open(yearsFile))
    genres = {k: genres[k] for k in genres if len(genres[k])!=0}
    years = {k: years[k] for k in years if len(years[k])!=0}

    songs = {}
    with open(csvFile) as inputFile:
        reader = csv.reader(inputFile)
        reader.next() # Skips header

        songCount = len(list(reader))
        counter = 1
        failureCount = 0
        inputFile.seek(0)
        reader.next() # Skips header
        for row in reader:
            if len(row) >= 4:
                try:
                    [uri, title, artist, album] = row[:4]
                    duration = row[6]
                except Exception as e:
                    print "Error parsing row: " + str(row)

                #print "Processing " + str(counter) + " of " + str(songCount)
                counter = counter + 1
                year = ""
                try:
                    year = years[uri]
                except Exception as e:
                    #print "Error getting year for: " + uri
                    failureCount = failureCount + 1
                    continue
                if year == "":
                    continue

                genre = []
                try:
                    genre = genres[uri]
                except Exception as e:
                    #print "Error getting genre for: " + uri
                    failureCount = failureCount + 1
                    ##continue

                songs[uri] = makeSong(title, artist, album, genre, duration, year)

    #print "Failed to find all information for " + str(failureCount) + " of " + str(songCount) + " files."
    return songs


# Combine the song information dictionary with a the lyrics from chartlyrics.com. After stripping
# stop words, add the total number of words in the song and the list of all swear words
def analyzeLyrics(songInfo, swearFile, lyricsFile, stopWordFile):

    with open(swearFile, 'r') as swearFile:
        swears = list(swearFile.read().splitlines())

    with open(stopWordFile, 'r') as stopFile:
        stopwords = [word for word in list(stopFile.read().splitlines()) if len(word) > 0 and word[0] != "#"]

    songLyrics = json.load(open(lyricsFile))
    results = { }
    for songId in songInfo:
        song = songInfo[songId]
        try:
            lyrics = songLyrics[songId]
        except Exception as e:
            #print "Song " + songId + " not found in lyrics file"
            continue

        lyrics = stripStopWords(lyrics, stopwords)
        #print songId + " : " + str(lyrics)
        if len(lyrics) == 0:
            continue;

        lyricsSwears = []
        for word in lyrics:
            if word in swears:
                lyricsSwears.append(word)


            # levenshtein disatance wasnt used for swear words because a lot of them are so short that 
            # doing so produces a lot of false positives, even with a distance of only one (eg shit shot shut)    
            '''
            for swear in swears:
                if levenshtein(word, swear) <= args.max:
                    swearCount = swearCount + 1
                    print word + " - " + swear + " distance = " + str(levenshtein(word, swear))
                    continue
            '''
        song["swear-words"] = lyricsSwears
        song["word-count"] = len(lyrics)
        results[songId] = song
        #print songId + " : " + str(song["year"]) + ", " + str(lyricsSwears)

    return results

# Generate a dictionary of song information and write it to a JSON file.
def main():
    args = parseArgs()
    
    songInfo = generateSongInfo(args.csv, args.genres, args.years)
    songInfo = analyzeLyrics(songInfo, args.swears, args.lyrics, args.stop)

    if len(songInfo) > 0:
        with open(args.results, "w") as infoFile:
            json.dump(songInfo, infoFile)

    allSwears = set()
    swearsByYear = {}
    for songId in songInfo:
        song = songInfo[songId]
        yearSwears = song["swear-words"]
        allSwears.update(yearSwears)
        year = song["year"]
        try:
            swearsByYear[year] += len(yearSwears)
        except Exception as e:
            swearsByYear[year] = len(yearSwears)

    # Prints statistics
    print "Number of songs:", len(songInfo)
    print "Number of swear words:", len(allSwears)
    print "Swear words by year:"
    for year in sorted(swearsByYear):
        print "  " + str(year) + ": " + str(swearsByYear[year])

if __name__ == "__main__":
    main()