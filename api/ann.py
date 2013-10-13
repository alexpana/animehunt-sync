from api.abstract import AbstractAPI


class AnimeNewsNetwork(AbstractAPI):
    _URL_LIST_ALL_ANIMES = "http://www.animenewsnetwork.com/encyclopedia/reports.xml?id=155&nlist=all&type=anime"

    # Requires the ID of the anime
    _URL_ANIME = "http://cdn.animenewsnetwork.com/encyclopedia/api.xml?anime=%s"

    _INTERNAL_CACHE = {}

    def __init__(self):
        AbstractAPI.__init__(self, __name__)

    def titles(self, title=None):
        if not 'titles' in self._INTERNAL_CACHE:
            self._INTERNAL_CACHE['titles'] = self._retrieve_titles()
        return self._INTERNAL_CACHE['titles']

    def anime(self, **kwargs):
        if 'title' in kwargs:
            return self._anime_by_title(kwargs['title'])
        if 'id' in kwargs:
            return self._anime_by_id(kwargs['id'])

    def _anime_by_title(self, title):
        raise NotImplementedError("")

    def _anime_by_id(self, anime_id):
        xml_response = self._http_request(self._URL_ANIME % anime_id)
        xml_root = self._parse_xml(xml_response)
        anime = {}
        anime['title'] = unicode(xml_root.xpath(".//info[@type='Main title']/text()")[0])
        anime['synonyms'] = map(lambda x: unicode(x),
                                xml_root.xpath(".//info[@type='Alternative title']/text()") + [anime['title']])
        anime['genres'] = str(xml_root.xpath(".//info[@type='Genres']/text()"))
        anime['plot_summary'] = unicode(self._first_element(xml_root.xpath(".//info[@type='Plot Summary']/text()"), ""))
        anime['episode_count'] = int(
            self._first_element(xml_root.xpath(".//info[@type='Number of episodes']/text()"), 0))
        return anime

    def _first_element(self, element_list, default):
        if len(element_list) == 0:
            return default
        else:
            return element_list[0]

    def _retrieve_titles(self):
        xml_response = self._http_request(self._URL_LIST_ALL_ANIMES)
        xml_root = self._parse_xml(xml_response)
        return map(lambda x: (int(x.xpath("id/text()")[0]), x.xpath("name/text()")[0]), xml_root.xpath(".//item"))