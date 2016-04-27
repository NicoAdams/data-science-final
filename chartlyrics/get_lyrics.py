# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import json
import time
import util
from chartlyrics_interface import ChartLyricsInterface

def main():
    interface = ChartLyricsInterface()
    songs = json.load(open('../data/songs.txt','rb'))
    try:
        lyrics = json.load(open('../data/lyrics.txt','rb'))
    except ValueError:
        # JSON throws a ValueError if the lyrics file is empty
        lyrics = {}
    
    try:
        count = 0
        for (uid, song) in songs.items():
            count += 1
            
            # Skips the song if its lyrics have already been downloaded
            if uid in lyrics: 
                continue
            
            title = song["title"]
            artist = song["artist"]
            
            # Generates possible titles to try
            possibleTitles = util.possibleNames(title)
            result = ""
            success = False
            for pt in possibleTitles:
                time.sleep(.5)
                result = interface.search_lyric_direct(artist, pt)
                if result is not None:
                    success = True
                    break
            
            lyrics[uid] = ("" if result is None else result.encode('utf-8'))
            
            successSymbol = "O" if success else "X"
            print successSymbol, count, title, ":", artist
    except Exception as e:
        print e
    finally:
        with open('../data/lyrics.txt', "w+") as f:
           json.dump(lyrics, f)

if __name__ == "__main__":
    main()
