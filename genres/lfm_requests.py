# Imports the parent directory
import inspect, os, sys
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import requests
import xml_parse

apiKey = "5da947c52b1de7e8daff6141a97a3af7"
baseUrl = "http://ws.audioscrobbler.com/2.0/"
timeout = 12
maxRequests = 1

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
	return tag['count'] >= 5

def getSignificantTags(topTagsTree):
	# Returns the most significant tag names for the given track
	tagTrees = topTagsTree.getchildren()[0].getchildren()
	tags = map(parseTag, tagTrees)
	
	# Processing step: Correlating names & combining counts
	
	tags = filter(significantTag, tags)
	return tags

def requestSignificantTags(trackName, artistName):
	r = requestTrackTopTags(trackName, artistName)
	rTree = xml_parse.parse(r.text.encode('utf-8'))
	return getSignificantTags(rTree)

