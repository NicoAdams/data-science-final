import csv
import json
import inspect
import os
import requests
import sys
import time
import re

# Imports the parent directory
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from util import levenshtein

baseURL = 'https://api.discogs.com/'
token = 'vXzDATLgZEbBAtEIeKGGPSmTdbifzmHCZYPaDAPD'
queryHeaders = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12) AppleWebKit/602.1.26 (KHTML, like Gecko) Version/9.2 Safari/602.1.26',
    'Content-Type': 'application/json'
}
albumArtistPair = {}

#********* Just for clairity, xxx_name is the name pulled from the csv file, and xxx_title is the name in discogs 

'''
{
    (album, artist) = year
}

get artist ID:
https://api.discogs.com/database/search?artist=tom%20waits&token=vXzDATLgZEbBAtEIeKGGPSmTdbifzmHCZYPaDAPD

"results": [
    {
        "thumb": "xxxx", 
        "title": "Tom Waits", 
        "uri": "/artist/82294-Tom-Waits", 
        "resource_url": "https://api.discogs.com/artists/82294", 
        "type": "artist", 
        "id": 82294
    },
    ...

info['results'][0].id => 82294


get all albums by artist 82294:
https://api.discogs.com/artists/82294/releases

?q=shamir+ratchet&type=all

https://api.discogs.com/database/search?q=shamir+ratchet&type=all&token=vXzDATLgZEbBAtEIeKGGPSmTdbifzmHCZYPaDAPD

https://api.discogs.com/database/search?album=840451&token=vXzDATLgZEbBAtEIeKGGPSmTdbifzmHCZYPaDAPD



'''

artistNumber = re.compile(" \([0-9]+\)")

def processArtistName(artistName):
    # Processes the artist name to get around Discog's conventions (removes trailing numbers)
    m = artistNumber.search(artistName)
    if m:
        artistName = artistName[:m.start()]
    return artistName

def artistAlbumSearch(artistName, albumName):
    # Searches for both an artist and an album
    url = baseURL + 'database/search?q='
    url += 'artist=' + artistName
    url += '&releases=' + albumName
    url += '&token=' + token
    response = requests.get(url, headers=queryHeaders)

def yearFromAristAndAlbum(artistName, albumName, maxDistance):
    ''' https://api.discogs.com/database/search?q=shamir+ratchet&type=all&token=vXzDATLgZEbBAtEIeKGGPSmTdbifzmHCZYPaDAPD
    '''
    url = baseURL + 'database/search?q='
    url += artistName + "+" + albumName
    url += "&type=all"
    url += '&token=' + token
    response = requests.get(url, headers=queryHeaders)
    #print url
    #print response

    json_info = json.JSONDecoder().decode(response.text)

    if 'results' not in json_info:
        return ''
    results = json_info['results']
    if len(results) == 0:
        return ''
    albumName = albumName.lower()
    artistName = artistName.lower()
    
    for album in results:
        title = album['title']
        if title is "":
            continue
        title = title.split(' - ')
        if len(title) == 1:
            continue
        tempArtist = processArtistName(title[0]).encode('utf-8').lower()
        tempAlbum = title[1].encode('utf-8').lower()
        #print "raw name = " + title[0]
        #print "processed name = " + tempArtist
        #print "album = " + tempAlbum

        if levenshtein(tempArtist, artistName) >= maxDistance:
            continue
        if levenshtein(tempAlbum, albumName) >= maxDistance:
            continue

        if 'year' not in album:
            continue
        year = album['year']
        if year is not "":
            return int(year)

    return None


        

def artistInfo(artistName):

    url = baseURL + 'database/search?q=artist=' + artistName
    url += '&token=' + token
    response = requests.get(url, headers=queryHeaders)
    #print url

    json_info = json.JSONDecoder().decode(response.text)

    if 'results' not in json_info:
        return ''
    results = json_info['results']
    if len(results) == 0:
        return ''

    return results
    ##artist_id = results[0]['id']

def artistAlbums(artist_id, album_name, maxDistance):
    """
    find data 
    look through albums 
    if album is close enough 
    pass album info to albumYear
    else  """

    url = baseURL + 'artists/' + str(artist_id) + '/releases'
    url += '?token=' + token + '&per_page=100'

    page_number = 1

    while True:
        queryUrl = url + '&page=' + str(page_number)
        response = requests.get(queryUrl, headers=queryHeaders)
        #print "requested: " + response.url

        json_info = json.JSONDecoder().decode(response.text)

        """print "json_info =  " + str(json_info)"""

        if 'releases' not in json_info:
            return ''
        album_list = json_info['releases']
        if len(album_list) == 0:
            return ''

        year = findAlbum(album_list, album_name, maxDistance)
        if year != '':
            return year
        page_number += 1


def findAlbum(album_list, album_name, maxDistance):
    for album in album_list:
        album_title = album['title'].encode('utf-8').lower()
        #print album_name  + ", " + album_title
        if levenshtein(album_name, album_title) <= maxDistance:
            return album['year']
    return '' # failure!

def processAlbum(artist_name, album_name, maxDistance):
    info = artistInfo(artist_name)
    if info == '':
        print 'Artist ' + artist_name + ' not found!!'
        return
    print 'Artist ' + artist_name
    artist_id = ''
    for artist_data in info:
        artist_title = artist_data['title'].encode('utf-8').lower()
            ##if levenshtein(artist, artist_name) <= maxDistance:
        artist_id = artist_data['id']
        if artist_id is not '':
            year = artistAlbums(artist_id, album_name, maxDistance)
            if year is not '':
                albumArtistPair[(album_name, artist_name)] = year
                break
    return year

def main():
    if len(sys.argv) < 3:
        print 'Usage: python ' + sys.argv[0] + 'artist album [maxDistance]'
        return
        
    rfile = sys.argv[1]
    wfile = sys.argv[2]

    if len(sys.argv) >= 4:
        maxDistance = int(sys.argv[3])
    else:
        maxDistance = 0

    '''
    open csv file
    for line in file:
        artist = line[xx]
        album = line[yyy]
        if (album, artist) in albumArtistPair:
            year = albumArtistPair[(album, artist)]
        else:
            look up year in discogs

        uuid = line[xx]
        write info file
    '''
    csvfile = open(rfile, 'rb') # opens the csv file    
    try:
        has_header = csv.Sniffer().has_header(csvfile.read(1024))
        csvfile.seek(0)  # rewind
        reader = csv.reader(csvfile)  # creates the reader object
        if has_header:
            next(reader)  # skip header row

        jsondata = {}
        failedsearches = {}

        for row in reader:   # iterates the rows of the file in orders
            artist = row[2]
            album = row[3]
            print "searching for: " + artist + " -- " + album
            uid = row[0]
            if (album, artist) in albumArtistPair:
                year = albumArtistPair[(album, artist)]
            else:
                year = yearFromAristAndAlbum(artist, album, maxDistance)
                if year is None:
                    year = ""
                    print artist + ", " + album + ", uid: " + uid + " not found"
                #year = processAlbum(artist, album, maxDistance)

            ##jsondata = {"uid": uid, "year": year}
            jsondata[str(uid)] = str(year)
            if year is "":
                failedsearches[str(uid)] =  {"artist": artist, "album": album}

            ##json.dump(jsondata, jsonfile)

    finally:
        jsonfile = open(wfile, 'w') 
        json.dump(jsondata, jsonfile)
        jsonfile.close()

        jsonfile = open("FAILED - " + wfile, 'w') 
        json.dump(failedsearches, jsonfile)
        jsonfile.close()

        csvfile.close()      # closing

    print str(year)



if __name__ == '__main__':
    main()
