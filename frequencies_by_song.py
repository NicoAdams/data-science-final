import ast

def main():
    f = open('./lyrics/dictionaries/10000.txt', 'r').read()
    lyrics = ast.literal_eval(f)
    # counter=0
    # to_remove = []
    # lyrics = lyric

    words_of_interest = open('words_of_interest.txt','r').read().splitlines()
    # print words_of_interest
    word_dict = {}
    for song in lyrics:
        word_dict[song] = []
        # print lyrics[song]
        for word in lyrics[song].split():
            # print word
            for curse in words_of_interest:
                # print curse
                # print word
                if curse in word:
                    # print curse
                    word_dict[song].append(curse)
                    # print word
        # for word in words_of_interest:
    print word_dict

# def process(dictionary):
#     for entry in dictionary:






if __name__ == "__main__":
    # lyr = 
	main()
