from api import API

__author__ = 'Alex'


class AnimeSeason(API):
    URL_TITLES = "http://www.animeseason.com/anime-list/"

    # Requires the title of the anime, formatted
    URL_ANIME = "http://www.animeseason.com/%s/"

    def __init__(self):
        API.__init__(self, __name__)
        pass

    def titles(self):
        return self._parse_titles(self._http_request(AnimeSeason.URL_TITLES))

    def anime(self, title):

        pass

    def _parse_titles(self, html):
        root_element = self._parse_html(html)
        return map( lambda x: (x.text, x.attrib['href']),root_element.xpath(".//ul[@class='series_alpha']/li/a"))