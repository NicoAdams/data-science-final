# General utility code

def levenshtein(s1, s2):
    """ Implementation of Levenshtein edit distance
    Lifted from https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python
    """
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    
    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def splitListOn(l, splitString):
    """ Splits each string in a list, then joins all results into a single list
    Eg. ["a:b", "c:d"], ":" -> ["a", ":b", "c", ":d"]
    """
    newList = []
    for item in l:
        isplit = item.split(splitString)
        for i in range(len(isplit)):
            toAdd = isplit[i]
            if i > 0:
                toAdd = splitString + toAdd
            newList.append(toAdd)
    return newList

def possibleNames(name):
    """ Obtains a set of possible names to try from a given track or album name
    
    Normal name first. Then removes parenthetical statements (eg.
    "(Remastered)", "(Deluxe)") and hyphenated statements (eg.
    " - Remastered", " - Deluxe)
    """
    nameComponents = [name]
    nameComponents = splitListOn(nameComponents, " (")
    nameComponents = splitListOn(nameComponents, " - ")
    possibleNames = []
    for i in range(len(nameComponents), 0, -1):
        possibleNames.append("".join(nameComponents[:i]))
    return possibleNames