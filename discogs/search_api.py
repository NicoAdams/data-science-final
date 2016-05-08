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

artistNumber = re.compile(" \([0-9]+\)", re.UNICODE)
def processArtistName(artistName):
    # Processes the artist name to get around Discog's conventions (removes trailing numbers)
    try:
        artistName = re.sub(artistNumber, '', artistName).strip()
    finally:
        return artistName

trailingParens = re.compile(" \(([^\)]+)\)", re.UNICODE)
def stripParens(albumName):
    # Processes the album name to remove trailing "(...)"
    try:
        albumName = re.sub(trailingParens, '', albumName)
    finally:
        return albumName

trailingBrackets = re.compile(" \[([^\)]+)\]", re.UNICODE)
def stripBrackets(albumName):
    # Processes the album name to remove trailing "[...]"
    try:
        albumName = re.sub(trailingBrackets, '', albumName)
    finally:
        return albumName

def stripAfterDash(albumName):
    offset = albumName.find('-')
    if offset:
        albumName = albumName[:offset]
    return albumName.strip()

def artistAlbumSearch(artistName, albumName):
    # Searches for both an artist and an album
    url = baseURL + 'database/search?q='
    url += 'artist=' + artistName
    url += '&releases=' + albumName
    url += '&token=' + token
    response = requests.get(url, headers=queryHeaders)

def searchAlbumInfo(results, albumName, artistName, maxDistance, albumProcessor):
    #print results

    originalAlbumName = albumName.encode('utf-8')

    albumName = albumName.lower()
    artistName = artistName.lower()

    if albumProcessor != None:
        albumName = albumProcessor(albumName)

    for album in results:
        #print album
        title = album['title'].encode('utf-8')
        if title is "":
            continue
        title = title.split(' - ')
        if len(title) == 1:
            continue
        tempArtist = processArtistName(title[0]).lower()
        tempAlbum = title[1].lower()

        '''
        print "full name = " + album['title']
        print "full name = " + album['title']
        print "split name = " + str(album['title'].split(' - '))
        print "raw name = " + title[0]
        print "processed name = " + tempArtist
        print "album = " + tempAlbum
        print "levenshtein('" + tempArtist + "', '" + artistName + "') = " + str(levenshtein(tempArtist, artistName))
        print "levenshtein('" + tempAlbum + "', '" + albumName + "') = " + str(levenshtein(tempAlbum, albumName))
        '''
        artist = tempArtist
        if levenshtein(tempArtist, artistName) >= maxDistance:
            continue

        if levenshtein(tempAlbum, albumName) >= maxDistance:
            continue

        if 'year' not in album:
            continue
        year = album['year'].encode('utf-8')
        if year is not "":
            if albumProcessor != None:
                print "   - selected '" + tempAlbum + "' when searching for '" + originalAlbumName + "'"
            return int(year)

    return None

def processAlbumList(results, albumName, artistName, maxDistance):
    
    year = searchAlbumInfo(results, albumName, artistName, maxDistance, None)
    if year != None:
        return year

    # no match, look through the results again ignoring "(...)" after the album name
    # eg. One Of These Nights (Remastered)
    #print "No match, trying again with relaxed album name"
    year = searchAlbumInfo(results, albumName, artistName, maxDistance, stripParens)
    if year != None:
        return year

    # no match, look through the results again ignoring "[...]" after the album name
    # eg. R&G (Rhythm & Gangsta): The Masterpiece [Explicit Version]
    #print "No match, trying again with relaxed album name"
    year = searchAlbumInfo(results, albumName, artistName, maxDistance, stripBrackets)
    if year != None:
        return year

    # no match, look through the results again ignoring everything after the first "-" in the album 
    # this is useful for album names like Weezer's "Pinkerton - Deluxe Edition"
    #print "No match, trying again with relaxed album name"
    year = searchAlbumInfo(results, albumName, artistName, maxDistance, stripAfterDash)

    return year

def yearFromAristAndAlbum(artistName, albumName, maxDistance):
    url = baseURL + 'database/search?q='
    url += artistName + "+" + albumName
    url += "&type=all"
    url += '&token=' + token
    url += '&per_page=100'
    response = requests.get(url, headers=queryHeaders)
    #print url
    #print response

    json_info = json.JSONDecoder().decode(response.text)

    if 'results' not in json_info:
        return ''
    results = json_info['results']
    if len(results) == 0:
        return ''
    
    year = processAlbumList(results, albumName, artistName, maxDistance)

    # don't call more than 2 times per second
    time.sleep(1/2)

    return year

def yearFromAlbumNameOnly(artistName, albumName, maxDistance):
    url = baseURL + 'database/search?q='
    url += albumName
    url += "&type=all"
    url += '&token=' + token
    url += '&per_page=100'
    response = requests.get(url, headers=queryHeaders)

    #print url
    #print response

    json_info = json.JSONDecoder().decode(response.text)

    if 'results' not in json_info:
        return ''
    results = json_info['results']
    if len(results) == 0:
        return ''

    year = processAlbumList(results, albumName, artistName, maxDistance)

    # don't call more than 2 times per second
    time.sleep(1/2)

    return year

def yearFromArtistNameOnly(artistName, albumName, maxDistance):
    url = baseURL + 'database/search?q='
    url += artistName
    url += "&type=all"
    url += '&token=' + token
    url += '&per_page=100'
    response = requests.get(url, headers=queryHeaders)

    #print "No match, searching by album name only"
    #print response

    json_info = json.JSONDecoder().decode(response.text)

    if 'results' not in json_info:
        return ''
    results = json_info['results']
    if len(results) == 0:
        return ''

    year = processAlbumList(results, albumName, artistName, maxDistance)

    # don't call more than 2 times per second
    time.sleep(1/2)

    return year

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

def albumYearForWriting(uid, year):
    return '"{0}" : "{1}",'.format(uid.encode('utf-8'), str(year).encode('utf-8'))

def main():
    if len(sys.argv) < 3:
        print 'Usage: python ' + sys.argv[0] + ' album_csv_file results_file [maxDistance]'
        return
        
    dataFile = sys.argv[1]
    resultsFile = sys.argv[2]

    if len(sys.argv) >= 4:
        maxDistance = int(sys.argv[3])
    else:
        maxDistance = 0

    jsondata = {}

    failFileName = resultsFile.split('.')[0]
    failedSearchFile = open("FAILED - " + failFileName + ".csv", 'a') 
    failureWriter = csv.writer(failedSearchFile)

    csvfile = open(dataFile, 'rb') # opens the csv file    
    try:
        reader = csv.reader(csvfile)
        reader.next()
        for row in reader:
            artist = unicode(row[2], 'utf-8')
            album = unicode(row[3], 'utf-8')
            uid = unicode(row[0], 'utf-8')
            print "searching for: " + artist + " -- " + album

            if (album, artist) in albumArtistPair:
                year = albumArtistPair[(album, artist)]
            else:
                year = yearFromAristAndAlbum(artist, album, maxDistance)

                if year is None:
                    year = yearFromAlbumNameOnly(artist, album, maxDistance)

                if year is None:
                    shortAlbumName = stripParens(album)
                    year = yearFromAlbumNameOnly(artist, shortAlbumName, maxDistance)

                if year is None:
                    shortAlbumName = stripAfterDash(album)
                    year = yearFromAlbumNameOnly(artist, shortAlbumName, maxDistance)

                if year is None:
                    # no match, try the "artist name" only up to a comma, eg. "Snoop Dogg, Pharrell Williams"
                    splitArtist = artist.split(',')
                    if len(splitArtist) > 1:
                        year = yearFromAristAndAlbum(splitArtist[0], album, maxDistance)

                if year is None:
                    year = ""
                    print "Not Found: " + artist + ", " + album + ", uid: " + uid

            jsondata[str(uid)] = str(year)

            if year is "":
                failureWriter.writerow(row)

    finally:
        jsonfile = open(wfile, 'w') 
        json.dump(jsondata, jsonfile)
        jsonfile.close()

        jsonfile.write("}\n");
        jsonfile.close()
        failedSearchFile.close()

        csvfile.close()      # closing

if __name__ == '__main__':
    main()
