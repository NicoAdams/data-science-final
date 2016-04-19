# Searches the API for an artist

import requests, json

baseURL = 'https://api.discogs.com/'
token = 'vXzDATLgZEbBAtEIeKGGPSmTdbifzmHCZYPaDAPD'

def search(artistName):
	url = baseURL+'database/search?q=artist='+artistName
	url += '&token='+token
	r = requests.get(url)
	d = json.JSONDecoder()
	return d.decode(r.text)
