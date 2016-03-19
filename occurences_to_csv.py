import ast
import csv

def main():
    f = open('occurences.txt', 'r').read()
    dictionary = ast.literal_eval(f)
    number = {}
    song_d = {}
    for song in dictionary:
        for di in dictionary[song]:
            # print di
            number[di] = 0
            song_d[di] = 0
    for song in dictionary:
        for di in dictionary[song]:
            # print di
            # number[di] += 1
            if dictionary[song][di] > 0:
                number[di] += dictionary[song][di]
                song_d[di] += 1
    # print number


    with open('curses.csv', 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["curse", "occurences", "songs"])
        for entry in number:
            writer.writerow([entry, number[entry], song_d[entry]])



if __name__ == "__main__":
    main()
