import matplotlib.pyplot as plt
import json
import numpy as np

def plot_genre(data, genre):
    '''
    plots lyric sentiment vs title sentiment for a given genre, coloring the points with a unique color
    :param data: the full dataset
    :param genre: genre to be plotted
    :return: handle to the plot, used for legend formatting
    '''
    genre_data = [x for x in data if genre in x[2]]
    handle, = plt.plot([row[0] for row in genre_data], [row[1] for row in genre_data], 'o', label=genre)
    return handle

def hist_genre(data, genre):
    '''
    plots distribution of lyric sentiment for a given genre
    :param data: the full dataset
    :param genre: the genre to be plotted
    :return: handle to the plot, used for legend formatting
    '''
    genre_data = [x[0] for x in data if genre in x[2]]
    n, b, p = plt.hist(genre_data, 10, alpha=0.5, normed=True, label=genre)
    mean = np.mean(genre_data)
    plt.plot((mean, mean), (0, max(n)), '-', linewidth=3)

def main():
    #input files
    lyric_sentiment_filename = "./sentiment/lyric_sentiment.txt"
    title_sentiment_filename = "./sentiment/title_sentiment.txt"
    genre_filename = "./data/genres.txt"

    #jsons parsed from file
    lyric_sentiment_json = json.loads(open(lyric_sentiment_filename, 'r').read())
    title_sentiment_json = json.loads(open(title_sentiment_filename, 'r').read())
    genre_json = json.loads(open(genre_filename, 'r').read())

    #formatting dataset
    data = [(val, title_sentiment_json[key], map(lambda genre: str(genre).lower(), genre_json[key]))
            for key, val in lyric_sentiment_json.items()
            if key in title_sentiment_json and key in genre_json]

    #genres to be plotted
    genres = ['death metal', 'country']

    #plotting title sentiment vs lyric sentiment for each genre
    handles = [plot_genre(data, genre) for genre in genres]
    plt.legend(handles=handles)
    plt.xlabel('lyric sentiment')
    plt.ylabel('title title_sentiment')
    plt.show()

    #plotting histogram of lyric sentiment for each genre
    for genre in genres:
        hist_genre(data, genre)
    plt.legend(handles=handles)
    plt.xlabel('lyric sentiment')
    plt.show()

    #box and whisker plot for each genre
    bnwdata = [[x[0] for x in data if genre in x[2]] for genre in genres]
    plt.boxplot(bnwdata)
    plt.xticks(range(1, len(genres) + 1), genres)
    plt.xlabel('genre')
    plt.ylabel('lyric sentiment')
    plt.show()

if __name__ == "__main__":
    main()