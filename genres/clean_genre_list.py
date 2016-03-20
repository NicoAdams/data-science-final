""" Cleans the genre list in genre_list

The goal of this cleaning process is to generate as many potential genre names
as possible, with no penalty for producing names that aren't genres
"""

import codecs

def splitStrings(strList, splitOn, includeOrig):
	# Splits each string in a list of strings on a split string
	# includeOrig: True if should include the original (unsplit) string in the new list
	newList = []
	def addFunc(s, newList):
		sSplit = s.split(splitOn)
		newList.extend(sSplit)
		if includeOrig and len(sSplit) >= 2:
			newList.append(s)
	map(lambda s: addFunc(s, newList), strList)
	return newList

def replaceStrings(strList, old, new, includeOrig):
	# Replaces all instances of string "old" with "new" in a string list
	# includeOrig: True if should include the original (unreplaced) string in the new list
	newList = []
	def addFunc(s, newList):
		sRep = s.replace(old, new)
		newList.append(sRep)
		if includeOrig and s!=sRep:
			newList.append(s)
	map(lambda s: addFunc(s, newList), strList)
	return newList

def main():
	inFile = "genre_list"
	outFile = "genre_list_clean"
	
	allGenres = []
	
	fin = codecs.open(inFile, encoding="utf8")
	for line in fin:
		# Skips initial comments
		if line and line[0] == "#":
			continue
		
		line = line.lower()
		genres = [line]
		
		# SPLITS
		
		# Splits on space. Includes original strings
		# "Southern Rock" -> ["Southern", "Rock", "Southern Rock"] 
		genres = splitStrings(genres, " ", True)
		
		# Splits on slash. Includes original strings
		# "Alt/Indie" -> ["Alt", "Indie", "Alt/Indie"] 
		genres = splitStrings(genres, "/", True)
		
		# REPLACEMENTS
		
		# Replaces "&" with "and". Keeps original
		genres = replaceStrings(genres, "&", "and", True)
		
		# Replaces unicode right single quotation mark with '. Discards original
		genres = replaceStrings(genres, u"\u2019", "'", False)
		
		# CLEANING
		
		# Removes whitespace
		genres = map(lambda s: s.strip(), genres)
		
		# Adds to grand list
		allGenres.extend(genres)
		
	# Filters list of duplicates and sorts
	allGenres = sorted(list(set(allGenres)))
	
	# Writes to file
	fout = codecs.open(outFile, mode="w+", encoding="utf8")
	for g in allGenres:
		fout.write(g+"\n")

if __name__ == '__main__':
	main()