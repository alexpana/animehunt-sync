from api.abstract import AbstractAPI


class AniDB(AbstractAPI):
    _ANIDB_ANIME_TITLES_SOURCE = "http://anidb.net/api/animetitles.xml.gz"

    _CACHE = {}

    def __init__(self):
        AbstractAPI.__init__(self, __name__)
        pass

    def anime(self, **kwargs):
        self._ensure_cache_integrity()
        if 'title' in kwargs:
            return self._CACHE['titles'][kwargs['title']]
        else:
            raise NotImplementedError('Indexing by ID is not yet implemented.')

    def titles(self, title=None):
        self._ensure_cache_integrity()
        return map(lambda x: (x, self._CACHE['titles'][x]['id']), self._CACHE['titles'])

    def synonyms(self, title):
        self._ensure_cache_integrity()
        return map(lambda x: x['title'], self._CACHE['titles'][title]['all'])

    def _ensure_cache_integrity(self):
        if 'titles' not in self._CACHE:
            anidb_response = self._http_request(AniDB._ANIDB_ANIME_TITLES_SOURCE)
            self._CACHE['titles'] = self._parse_titles_xml(anidb_response)

    def _parse_titles_xml(self, xml):
        root = self._parse_xml(xml)
        anime_titles = {}

        for anime in root:
            aid = anime.attrib['aid']
            main_title = ""
            main_jp_title = ""

            # {'title' -> str, 'type'->str, 'lang':str}}
            titles = []

            element_titles = {}
            main_titles = [
                anime.xpath(".//title[@type='official' and @xml:lang='en']"),
                anime.xpath(".//title[@type='syn' and @xml:lang='en']"),
                anime.xpath(".//title[@type='main']")]

            if len(main_titles[0]) > 0:
                element_titles["official-en"] = main_titles[0][0].text
            if len(main_titles[1]) > 0:
                element_titles["syn-en"] = main_titles[1][0].text
            if len(main_titles[2]) > 0:
                element_titles["main"] = main_titles[2][0].text

            if 'official-en' in element_titles.keys():
                main_title = element_titles['official-en']
            elif 'syn-en' in element_titles.keys():
                main_title = element_titles['syn-en']
            else:
                main_title = element_titles['main']

            if aid == '5101':
                pass

            for title in anime:
                titles.append({
                    'title': title.text,
                    'type': title.attrib['type'],
                    'lang': title.attrib['{http://www.w3.org/XML/1998/namespace}lang']})

            main_jp_title = element_titles['main']
            anime_titles[main_title] = (
                {'id': aid,
                 'jp': main_jp_title,
                 'all': titles})

        return anime_titles