import requests
import xml.etree.ElementTree as ET

class ChartLyricsInterface(object):
    '''
    Python interface for interacting with the ChartLyrics API
    '''
    prefix_url = 'http://api.chartlyrics.com/apiv1.asmx/'

    def __init__(self): pass

    def __api_call(self, command, argnames, args):
        '''
        Submits a call to the ChartLyrics API
        :param command: API call the user wishes to perform
        :param argnames: a list of argument names for the API call
        :param args: a list of arguments corresponding to each argument name
        :return: the response from the API if the call is successful, otherwise None
        '''
        assert len(argnames) == len(args), 'Number of argnames must match number of args'
        url = self.prefix_url + command + '?' + self.__format_query(argnames, args)
        try:
            r = requests.get(url)
            return r.text if r else None
        except:
            return None

    def __format_query(self, argnames, args):
        '''
        Formats a query
        :param argnames: a list of argument names for an API call
        :param args: a list of arguments corresponding to each argument name
        :return: a string formatted for the ChartLyrics API using the given argument names and values
        '''
        args = [arg.lower().strip().replace(' ', '%20') for arg in args]
        return '&'.join([argname + '=' + arg for argname, arg in zip(argnames, args)])

    def search_lyric(self, artist, song):
        '''
        Returns response from calling SearchLyric on the API
        :param artist: the artist to look for
        :param song: the song by the given artist to look for
        :return: xml returned from the API call
        '''
        xml = self.__api_call('SearchLyric', ['artist', 'song'], [artist, song])
        return xml

    def search_lyric_direct(self, artist, song):
        '''
        Returns response from calling SearchLyricDirect on the API
        :param artist: the artist to look for
        :param song: the song by the given artist to look for
        :return: the lyrics for the given song if the call is successful, otherwise None
        '''
        xml = self.__api_call('SearchLyricDirect', ['artist', 'song'], [artist, song])
        if xml is None:
            return None
        root = ET.fromstring(xml.encode('utf-8'))
        return root[-1].text

    def search_lyric_text(self, lyricText):
        '''
        Returns response from calling SearchLyricText on the API
        :param lyricText: lyric to look for
        :return: xml returned from the API call
        '''
        xml = self.__api_call('SearchLyricText', ['lyricText'], [lyricText])
        return xml

    def get_lyric(self, lyricId, lyricCheckSum):
        '''
        Returns response from calling GetLyric on the API
        :param lyricId: unique lyric id to look for
        :param lyricCheckSum: lolidk
        :return: xml returned from the API call
        '''
        xml = self.__api_call('GetLyric', ['lyricId', 'lyricCheckSum'], [lyricId, lyricCheckSum])
        return xml

if __name__ == "__main__":
    interface = ChartLyricsInterface()
    print interface.search_lyric("Michael Jackson", "Bad")