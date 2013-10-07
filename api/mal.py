from api import API


class MyAnimeList(API):

    # Name of a power user
    _POWER_USER_NAME = "coty9090"

    # Url of a power user's anime list. Guaranteed to be large!
    _URL_POWER_USER_ANIME_LIST = "http://myanimelist.net/malappinfo.php?u=%s&status=all&type=anime" % _POWER_USER_NAME

    # Requires a partial or full anime TITLE.
    _URL_ANIME_SEARCH_QUERY = "http://myanimelist.net/api/anime/search.xml?q=%s"

    # Requires the anime ID and the anime TITLE
    _URL_ANIME_USERRECS = "http://myanimelist.net/anime/%s/%s/userrecs"

    # Requires the anime ID and the anime TITLE
    _URL_ANIME_MAIN = "http://myanimelist.net/anime/%s/%s/"

    def __init__(self, **settings):
        API.__init__(self, __name__)
        self.settings = settings

        if not 'username' in self.settings.keys():
            raise Exception("Username required")

        if not 'password' in self.settings.keys():
            raise Exception("Password required")

        self._auth = (settings['username'], settings['password'])

    def anime(self, title):
        """
        Returns the anime who's title is equal to the title parameter
        """
        url = MyAnimeList._URL_ANIME_SEARCH_QUERY % "+".join(title.split(" "))
        mal_response = self._http_request(url, self._auth)

        if mal_response != "":
            anime_list = self._parse_anime_search_result(mal_response)
            for current_anime in anime_list:
                if current_anime['title'] == title:
                    return current_anime

        return None

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

    def titles(self, title=None):
        if title is None:
            self.log.warn("Support for listing all titles is experimental and incomplete.")
            return self._all_titles()
        else:
            url = MyAnimeList._URL_ANIME_SEARCH_QUERY % "+".join(title.split(" "))
            mal_response = self._http_request(url, self._auth)
            anime_list = []
            if mal_response != "":
                anime_list = self._parse_anime_search_result(mal_response)
            return map(lambda x: x['title'], anime_list)

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

    def _all_titles(self):
        response = self._http_request(MyAnimeList._URL_POWER_USER_ANIME_LIST, self._auth)
        return self._parse_user_animelist_xml_result(response)

    def _parse_user_animelist_xml_result(self, xml):
        xml_root = API._parse_xml(xml)
        return map(lambda x: x.text, xml_root.xpath(".//series_title"))




