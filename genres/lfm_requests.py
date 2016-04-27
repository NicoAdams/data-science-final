# Allows importing from the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import requests
import xml_parse
import json
import time
import util

# Configuration data for Last.FM requests
apiKey = "5da947c52b1de7e8daff6141a97a3af7"
baseUrl = "http://ws.audioscrobbler.com/2.0/"
timeout = 12
maxRequests = 1

# Genre classification setup
genreFile = "./genre_list_clean"
tagSignificance = 10 # Minimum tag significance

# -- Requests --

def request(method, queries):
	# Generic form of an API request. Returns the parsed XML of a request
	queries.insert(0, ("method", method))
	queries.append(("api_key", apiKey))
	return requests.get(baseUrl, params=dict(queries), timeout=timeout)

def repeatedRequest(method, queries, maxReq=maxRequests):
	# Continues requesting until timeout. Set maxReq=-1 for unlimited requests
	numRequests = 0
	while True:
		numRequests += 1
		try:
			return request(method, queries)				
		except requests.exceptions.ConnectTimeout as e:
			if numRequests == maxRequests:
				raise e

def requestTrackInfo(trackName, artistName):
	# Gets info on the song given by songName, artistName
	method = "track.getInfo"
	queries = []
	queries.append(('track', trackName))
	queries.append(('artist', artistName))
	return repeatedRequest(method, queries)

def requestTrackTopTags(trackName, artistName):
	# Gets info on the song given by songName, artistName
	method = "track.getTopTags"
	queries = []
	queries.append(('track', trackName))
	queries.append(('artist', artistName))
	return repeatedRequest(method, queries)

def requestTagInfo(tagName):
	# Gets info and a description of a tag
	method = "tag.getInfo"
	queries = []
	queries.append(('tag', tagName))
	return repeatedRequest(method, queries)

# -- Data processing --

def parseTag(tagTree):
	# Returns a dict from xml representing a tag
	tagInfo = tagTree.getchildren()
	count = int(tagInfo[0].text)
	name = tagInfo[1].text
	url = tagInfo[2].text
	return {'count':count, 'name':name, 'url':url}

def significantTag(tag):
	# Returns True if the tag is significant by count, else false
	return tag['count'] >= tagSignificance

def getGenres(tags):
	# Returns the tags from a tag list that are valid genres
	
	# Loads the genre list
	genresMaster = open(genreFile).readlines()
	# map(lambda s: s.strip(), genresMaster)
	for i in range(len(genresMaster)):
		genresMaster[i] = genresMaster[i].strip()
	genresMaster = set(genresMaster)
	
	genres = []
	for tag in tags:
		tagname = tag['name'].lower()
		if tagname in genresMaster:
			genres.append(tagname)
	return genres

def getSignificantTags(topTagsTree):
	# Returns the most significant tag names for the given track
	tagTrees = topTagsTree.getchildren()[0].getchildren()
	tags = map(parseTag, tagTrees)
	
	# Filters tags with low significance
	tags = filter(significantTag, tags)
	
	return tags

def requestSignificantTags(trackName, artistName):
	# Returns a 
	r = requestTrackTopTags(trackName, artistName)
	rTree = xml_parse.parse(r.text.encode('utf-8'))
	return getSignificantTags(rTree)

# -- Data compiling --

def requestGenresFromSong(trackName, artistName):
	""" Requests a song's tags from its info dictionary
	songInfo: A dictionary with fields "title" and "artist"
	"""
	tags = requestSignificantTags(trackName, artistName)
	return getGenres(tags)

def generateGenreData(songsFile, genresFile):
	""" Obtains the genres dataset from the songs dataset
	"""
	songsFileData = json.load(open(songsFile))
	
	genreData = json.load(open(genresFile))
	# try:
	print "Beginning"
	count = 0
	try:
		for songID in songsFileData:
			count += 1
			
			if songID in genreData:
				continue
			
			songInfo = songsFileData[songID]
			title = songInfo["title"]
			artist = songInfo["artist"]
			
			effTitle = title
			for possibleTitle in util.possibleNames(title):
				
				effTitle = possibleTitle
				
				genres = requestGenresFromSong(possibleTitle, artist)
				if len(genres) > 0:
					break
			
			genreData[songID] = genres
			
			print 
			print "--", count, "--"
			print title
			print effTitle
			print genres
			
			time.sleep(0.2)
	finally:
		with open(genresFile, "w+") as f:
			f.write(json.dumps(genreData))

if __name__ == "__main__":
	generateGenreData("../data/songs.txt", "../data/genres.txt")