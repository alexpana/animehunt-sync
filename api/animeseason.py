from api import API, Helper

__author__ = 'Alex'


class AnimeSeason(API):
    _URL_TITLES = "http://www.animeseason.com/anime-list/"

    # Requires the title of the anime, formatted
    _URL_ANIME_MAIN = "http://www.animeseason.com/%s/"

    _INTERNAL_CACHE = {'animes': {}, 'titles': {}}

    def __init__(self):
        API.__init__(self, __name__)
        pass

    def titles(self, title=None):
        all_titles = self._parse_titles(self._http_request(AnimeSeason._URL_TITLES))
        if title is None:
            return all_titles
        else:
            matching_titles = []
            for current_title in all_titles:
                current_title = self._sanitize_title(current_title)
                if Helper.canonic_matching(title, current_title):
                    matching_titles.append(current_title)
        return matching_titles

    def anime(self, title):
        if title not in self._INTERNAL_CACHE['animes']:
            response = self._http_request(self.url(title))
            self._INTERNAL_CACHE['animes'][title] = self._parse_anime(response)
        return self._INTERNAL_CACHE['animes'][title]

    def url(self, title):
        if not 'urls' in self._INTERNAL_CACHE:
            self.titles()

        if title in self._INTERNAL_CACHE['urls'].keys():
            return self._INTERNAL_CACHE['urls'][title]
        else:
            return None

    def recommendations(self, title):
        return self.anime(title)['recommendations']

    def _parse_titles(self, html):
        if not "urls" in AnimeSeason._INTERNAL_CACHE.keys():
            root_element = self._parse_html(html)
            titles = dict(
                map(lambda x: (x.text, x.attrib['href']), root_element.xpath(".//ul[@class='series_alpha']/li/a")))
            AnimeSeason._INTERNAL_CACHE["urls"] = titles
        return AnimeSeason._INTERNAL_CACHE["urls"].keys()

    def _parse_anime(self, html):
        root = self._parse_html(html)

        anime = {}

        # series info
        keys = root.xpath(".//dl[@id='series_info']/dt")
        values = root.xpath(".//dl[@id='series_info']/dd")
        for i in range(len(keys)):
            key = keys[i].text[0:-1].lower()
            if values[i].text is not None:
                value = values[i].text.strip()
            else:
                value = ""
            if key == 'title':
                anime['title'] = value
            if key == 'type':
                anime_type = map(lambda x: x.strip(), value.split(","))
                anime['type'] = anime_type[0]
                if len(anime_type) == 2:
                    anime['episodes'] = int(anime_type[1].split(' ')[0])
            if key == 'year':
                anime['year'] = value.split(' to ')
            if key == 'genre':
                anime['genre'] = map(lambda x: str(x), values[i].xpath(".//a/text()"))
            if key == 'status':
                anime['status'] = value

        # summary
        anime['summary'] = unicode(root.xpath(".//div[@class='content_bloc'][1]/p[1]/text()")[0])

        # rating
        anime['rating'] = int(root.xpath(".//div[@id='avg_rating'][1]/text()")[0][0:-1])

        # recommendations
        recommendation_titles = map(lambda x: str(x), root.xpath(".//div[@id='rec_scroll']//td/a/text()"))
        recommendation_ratings = map(lambda x: int(x), root.xpath(".//div[@id='rec_scroll']//td/text()")[1::2])
        anime['recommendations'] = map(
            lambda x: {'anime': x[0], 'count': x[1]}, zip(recommendation_titles, recommendation_ratings))

        # related
        if len(root.xpath(".//div[@id='relations']")) == 0:
            anime['relations'] = []
        else:
            relation_tokens = root.xpath(".//div[@id='relations']//tr[position() > 1]//text()[position() mod 3 != 2]")
            anime['relations'] = map(
                lambda x: {'name': x[0], 'relation': x[1]}, zip(relation_tokens[::2], relation_tokens[1::2]))

        return anime

    def _sanitize_title(self, title):
        """Changes the title slightly to improve it's identity"""
        return title.replace("(Movie)", "movie")