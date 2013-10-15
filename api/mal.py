import json
from api.abstract import AbstractAPI


class MyAnimeList(AbstractAPI):
    # Name of a power user
    _POWER_USER_NAME = "coty9090"

    # Url of a power user's anime list. Guaranteed to be large!
    _URL_POWER_USER_ANIME_LIST = "http://myanimelist.net/malappinfo.php?u=%s&status=all&type=anime" % _POWER_USER_NAME

    # Requires a partial or full anime TITLE.
    _URL_ANIME_SEARCH_QUERY = "http://myanimelist.net/api/anime/search.xml?q=%s"

    # Requires the anime ID and the anime TITLE
    _URL_ANIME_USERRECS = "http://myanimelist.net/anime/%s/%s/userrecs"

    # Requires the anime ID
    _URL_ANIME_MAIN = "http://myanimelist.net/anime/%d"

    # Requires the anime ID
    _URL_UNOFFICIAL_ANIME = "http://mal-api.com/anime/%s"

    def __init__(self, **settings):
        AbstractAPI.__init__(self, __name__)
        self.settings = settings

        if not 'username' in self.settings.keys():
            raise Exception("Username required")

        if not 'password' in self.settings.keys():
            raise Exception("Password required")

        self._auth = (settings['username'], settings['password'])

    def search(self, anime):
        pass

    def anime(self, **kwargs):
        if 'title' in kwargs:
            return self._get_anime_by_title(kwargs['title'])
        else:
            return self._get_anime_by_id(kwargs['id'])

    def recommendations(self, title):
        """
        Returns a list of recommendations for the anime matching title
        """
        anime_title = self.search_title(title)

        if anime_title is None:
            return []

        anime = self.anime(anime_title)
        url = self._URL_ANIME_USERRECS % (anime['id'], anime['title'])
        mal_response = self._http_request(url, self._auth)

        return self._parse_userrecs_html_result(mal_response)

    def url(self, title):
        anime = self.anime(title)
        return (self._URL_ANIME_MAIN % (anime['id'], anime['title'])).replace(" ", "%20")

    def experimental_titles(self, title=None):
        if title is None:
            return self._experimental_all_anime().keys()
        else:
            return self.titles(title)

    def experimental_anime(self, anime):
        return self._experimental_all_anime()[anime]

    def experimental_ids(self):
        return map(lambda x: self.experimental_anime(x)['id'], self.experimental_titles())

    def unofficial_anime(self, anime_id):
        result = self._http_request(self._URL_UNOFFICIAL_ANIME % str(anime_id))
        return self._parse_unofficial_anime(result)

    def titles(self, title=None):
        if title is None:
            self.log.debug("Retrieving all the titles from MAL is only experimentally supported through expr_titles.")
            return []
        else:
            url = MyAnimeList._URL_ANIME_SEARCH_QUERY % "+".join(title.split(" "))
            mal_response = self._http_request(url, self._auth)
            anime_list = []
            if mal_response != "":
                anime_list = self._parse_anime_search_result(mal_response)
            return map(lambda x: (x['title'], x['title']), anime_list)

    def _get_anime_by_id(self, anime_id):
        url = MyAnimeList._URL_ANIME_MAIN % anime_id
        mal_response = self._http_request(url, self._auth)
        return self._parse_anime_html(mal_response)

    def _get_anime_by_title(self, title):
        url = MyAnimeList._URL_ANIME_SEARCH_QUERY % "+".join(title.split(" "))
        mal_response = self._http_request(url, self._auth)
        if mal_response != "":
            anime_list = self._parse_anime_search_result(mal_response)
            for current_anime in anime_list:
                if current_anime['title'] == title:
                    return current_anime
        return None

    def _parse_anime_html(self, html):
        anime = {}
        root_element = self._parse_html(html)
        attr_spans = root_element.xpath(".//span[@class='dark_text']")
        for attr_span in attr_spans:
            if attr_span.text == "Type:":
                anime['type'] = attr_span.tail.strip()
            if attr_span.text == "Episodes:":
                anime['episode_count'] = int(attr_span.tail.strip())
            if attr_span.text == "Status:":
                anime['status'] = attr_span.tail.strip()
            if attr_span.text == "Aired:":
                anime['aired'] = attr_span.tail.strip()
            if attr_span.text == "Producers:":
                anime['producers'] = map(lambda x: x.text, attr_span.getparent().xpath(".//a"))
            if attr_span.text == "Genres:":
                anime['genres'] = map(lambda x: x.text.strip().lower(), attr_span.getparent().xpath(".//a"))
            if attr_span.text == "Duration:":
                anime['duration'] = attr_span.tail.strip()
            if attr_span.text == "Rating:":
                anime['rating'] = attr_span.tail.strip()

        anime['summary'] = root_element.xpath(".//h2[text()='Synopsis']")[0].tail.strip()

        anime['synonyms'] = map(lambda x: x.tail.strip(),
                                root_element.xpath(".//h2[text()='Alternative Titles']")[0].getparent().xpath(
                                    ".//div[@class='spaceit_pad']/span"))
        return anime

    def _parse_anime_search_result(self, xml):
        """
        Parses an xml containing a list of animes fetched from MAL
        """
        root_element = self._parse_html(xml)
        anime_list = []
        for anime_entry in root_element[0][0].getchildren():
            anime = {}
            for anime_attribute in anime_entry:
                anime[anime_attribute.tag] = anime_attribute.text
                if anime_attribute.tag == 'episodes':
                    anime[anime_attribute.tag] = int(anime_attribute.text)
                if anime_attribute.tag == 'synonyms':
                    if anime_attribute.text is not None:
                        anime[anime_attribute.tag] = anime_attribute.text.split("; ")
                    else:
                        anime[anime_attribute.tag] = []
            anime_list.append(anime)
        return anime_list

    def _parse_userrecs_html_result(self, html):
        """
        Parses the MAL userrecs page containing a list of recommendations
        """
        html_root = self._parse_html(html)

        recommendations = []

        recommendation_tds = html_root.xpath(".//div[@class='borderClass']//td[@valign='top'][2]")
        for td in recommendation_tds:
            try:
                recommendation = {
                    'anime': td[1][0][0].text,
                    'details': td[2][0].text,
                    'author': td[2][1][1].text}
                if len(td.getchildren()) == 5:
                    recommendation['count'] = int(td[3][0][0].text) + 1
                else:
                    recommendation['count'] = 1

                recommendations.append(recommendation)
            except:
                pass

        return recommendations

    def _experimental_ensure_cache(self):
        self._experimental_all_anime()

    def _experimental_all_anime(self):
        if 'experimental_titles' not in self.CACHE:
            response = self._http_request(MyAnimeList._URL_POWER_USER_ANIME_LIST, self._auth)
            self.CACHE['experimental_titles'] = self._parse_user_animelist_xml_result(response)
        return self.CACHE['experimental_titles']

    def _parse_user_animelist_xml_result(self, xml):
        xml_root = AbstractAPI._parse_xml(xml)
        animes = {}
        for anime_elem in xml_root.xpath(".//anime"):
            anime = {}
            anime['id'] = int(anime_elem.xpath(".//series_animedb_id/text()")[0])
            anime['title'] = unicode(anime_elem.xpath(".//series_title/text()")[0])
            synonyms_text = anime_elem.xpath(".//series_synonyms/text()")
            if len(synonyms_text) == 0:
                anime['synonyms'] = []
            else:
                anime['synonyms'] = anime_elem.xpath(".//series_synonyms/text()")[0].split("; ")
            anime['synonyms'] = filter(lambda x: x != '', anime['synonyms'])
            anime['type'] = int(anime_elem.xpath(".//series_type/text()")[0])
            anime['episode_count'] = int(anime_elem.xpath(".//series_episodes/text()")[0])
            anime['status'] = int(anime_elem.xpath(".//series_status/text()")[0])
            anime['start'] = str(anime_elem.xpath(".//series_start/text()")[0])
            anime['end'] = str(anime_elem.xpath(".//series_end/text()")[0])
            anime['image'] = str(anime_elem.xpath(".//series_image/text()")[0])
            animes[anime['title']] = anime

        return animes

    def _parse_unofficial_anime(self, json_value):
        anime = json.loads(json_value)
        anime['episode_count'] = anime['episodes']
        anime['summary'] = anime['synopsis']
        anime['synonyms'] = [anime['title']]
        for lang in anime['other_titles']:
            anime['synonyms'] += anime['other_titles'][lang]
        anime.pop('episodes', None)
        anime.pop('summary', None)
        return anime