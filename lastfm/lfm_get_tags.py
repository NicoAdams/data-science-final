import lfm_requests, sys

""" Command line tool to acquire song tags from Last.FM. Prints the top N tags for the song

To use, run:
	python lfm_get_tags.py trackName artistName [numTags]
"""

def main():
	if len(sys.argv) < 3:
		print "Usage: python lfm_get_tags.py trackName artistName [numTags]"
		return
		
	trackName = sys.argv[1]
	artistName = sys.argv[2]
	if len(sys.argv)>=4:
		numTags = int(sys.argv[3])
	else:
		numTags = -1
	
	tags = lfm_requests.requestSignificantTags(trackName, artistName)
	if numTags != -1:
		tags = tags[:min(len(tags), numTags)]
	print "-- Tags --"
	for t in tags: print t['count'], t['name']

if __name__ == "__main__":
	main()