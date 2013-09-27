from api import API


class MyAnimeList(API):
    # Requires a partial or full anime TITLE.
    _ANIME_SEARCH_QUERY = 'http://myanimelist.net/api/anime/search.xml?q=%s'

    # Requires the anime ID and the anime TITLE
    _ANIME_USERRECS_URL = "http://myanimelist.net/anime/%d/%s/userrecs"

    def __init__(self, **settings):
        API.__init__(self, __name__)
        self.settings = settings

        if not 'username' in self.settings.keys():
            raise Exception("Username required")

        if not 'password' in self.settings.keys():
            raise Exception("Password required")

        self._auth = (settings['username'], settings['password'])

    def search_anime(self, title):
        """
        Returns a list of animes that match the title
        """
        url = MyAnimeList._ANIME_SEARCH_QUERY % "+".join(title.split(" "))
        mal_response = self._http_request(url, self._auth)

        if mal_response != "":
            return self._parse_anime_search_result(mal_response)
        else:
            return []

    def recommendations(self, title):
        """
        Returns a list of recommendations for the anime matching title
        """
        anime_list = self.search_anime(title)
        anime = None
        for anime_entry in anime_list:
            if anime_entry['title'] == title:
                anime = (int(anime_entry['id']), anime_entry['title'])
                break

        if len(anime_list) == 0:
            self.log.error("No anime was found with that name.")
            return None
        elif len(anime_list) > 1 and anime is None:
            self.log.error("More than one anime was found and none matched the title perfectly.")
            self.log.error("Found titles: " + str(map(lambda x: x['title'], anime_list)))
            return None

        url = self._ANIME_USERRECS_URL % anime
        mal_response = self._http_request(url, self._auth)

        return self._parse_userrecs_html_result(mal_response)

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
            except: pass

        return recommendations