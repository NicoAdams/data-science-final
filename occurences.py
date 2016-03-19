import ast

def main():
    f = open('curse_list_dictionary.txt', 'r').read()
    curses = ast.literal_eval(f)
    # for curse in curses:
        # curses[curse]

    words_of_interest = open('words_of_interest.txt','r').read().splitlines()
    
    # end result:
    # dictionary with (key, value) (song, dictionary)
    # within each song's dictionary, (k, v) is (curse, occurences)

    other = {}
    for song in curses:
        # other[song] = {}
        # entry = other[song]
        occurences = {}
        for word in words_of_interest:
            occurences[word] = 0
        for entry in curses[song]:
            occurences[entry] += 1
            # print entry
        other[song] = occurences
    print other






if __name__ == "__main__":
	main()
