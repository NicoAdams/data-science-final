import csv
import time
from chartlyrics_interface import ChartLyricsInterface

def main():
    interface = ChartLyricsInterface()
    # csv_reader = csv.reader(open('200s_123songs.csv','rb'))
    csv_reader = csv.reader(open('songs_500.csv','rb'))
    next(csv_reader, None)
    dictionary = {}
    for song, artist in csv_reader:
        time.sleep(.5)
        key = song + " by " + artist
        toPrint =  interface.search_lyric_direct(artist, song)
        if toPrint is None:
            dictionary[key] = "Error, song not found on chartlyrics"
        else:
            dictionary[key] = toPrint.encode('utf-8')
    print dictionary

if __name__ == "__main__":
    main()
