import requests
import xml.etree.ElementTree as ET

class ChartLyricsInterface(object):

    prefix_url = 'http://api.chartlyrics.com/apiv1.asmx/'

    def __init__(self): pass

    def __api_call(self, command, argnames, args):
        assert len(argnames) == len(args), 'Number of argnames must match number of args'
        url = self.prefix_url + command + '?' + self.__format_query(argnames, args)
        print url
        r = requests.get(url)
        return r.text if r else None

    def __format_query(self, argnames, args):
        args = [arg.lower().strip().replace(' ', '%20') for arg in args]
        return '&'.join([argname + '=' + arg for argname, arg in zip(argnames, args)])

    def search_lyric(self, artist, song):
        xml = self.__api_call('SearchLyric', ['artist', 'song'], [artist, song])
        return xml

    def search_lyric_direct(self, artist, song):
        xml = self.__api_call('SearchLyricDirect', ['artist', 'song'], [artist, song])
        root = ET.fromstring(xml)
        return root[-1].text

    def search_lyric_text(self, lyricText):
        xml = self.__api_call('SearchLyricText', ['lyricText'], [lyricText])
        return xml

    def get_lyric(self, lyricId, lyricCheckSum):
        xml = self.__api_call('GetLyric', ['lyricId', 'lyricCheckSum'], [lyricId, lyricCheckSum])
        return xml

if __name__ == "__main__":
    interface = ChartLyricsInterface()
    print interface.search_lyric_direct("Michael Jackson", "Bad")