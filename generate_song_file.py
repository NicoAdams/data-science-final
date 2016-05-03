# Converts the song list csv file to the json songs file

import csv, json

def getUID(uriString):
	# return uriString.split(":")[2]
	return uriString

def makeSongObject(title, artist, album):
	return {"title": title, "artist": artist, "album": album}

def readSongs(csvFile):
	songs = {}
	
	with open(csvFile) as f:
		r = csv.reader(f)
		r.next() # Skips header
		
		for row in r:
			if len(row) >= 4:
				# Acquires the first 4 fields
				try:
					[uri, title, artist, album] = row[:4]
				except Exception as e:
					print row
					raise e
				songs[getUID(uri)] = makeSongObject(title, artist, album)
	return songs

def writeSongs(songs, jsonFile):
	with open(jsonFile, "w+") as f:
		json.dump(songs, f)

if __name__ == '__main__':
	songs = readSongs("data/datascience.csv")
	
	print len(songs)
	
	writeSongs(songs, "data/songs.txt")