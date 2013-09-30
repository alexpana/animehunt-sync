from api import API


class AniDB(API):
    _ANIDB_ANIME_TITLES_SOURCE = "http://anidb.net/api/animetitles.xml.gz"

    _CACHE = {}

    def __init__(self):
        API.__init__(self, __name__)
        pass

    def titles(self, title=None):
        self.validate_cache()
        return self._CACHE['titles'].keys()

    def synonyms(self, title):
        self.validate_cache()
        return self._CACHE['titles'][title]['all']

    def validate_cache(self):
        if 'titles' not in self._CACHE:
            anidb_response = self._http_request(AniDB._ANIDB_ANIME_TITLES_SOURCE)
            self._CACHE['titles'] = self._parse_titles_xml(anidb_response)

    def _parse_titles_xml(self, xml):
        root = self._parse_xml(xml)
        anime_titles = {}

        for anime in root:
            element_titles = {}
            titles = [
                anime.xpath(".//title[@type='official' and @xml:lang='en']"),
                anime.xpath(".//title[@type='syn' and @xml:lang='en']"),
                anime.xpath(".//title[@type='main']")]

            if len(titles[0]) == 1:
                element_titles["official-en"] = titles[0][0].text
            if len(titles[1]) == 1:
                element_titles["syn-en"] = titles[1][0].text
            if len(titles[2]) == 1:
                element_titles["main"] = titles[2][0].text

            entry = ["", ""]
            if 'official-en' in element_titles.keys():
                entry[0] = element_titles['official-en']
            elif 'syn-en' in element_titles.keys():
                entry[0] = element_titles['syn-en']
            else:
                entry[0] = element_titles['main']

            entry[1] = element_titles['main']
            anime_titles[entry[0]] = ({'jp': entry[1], 'all': map(lambda x: x.text, anime.getchildren())})
        return anime_titles