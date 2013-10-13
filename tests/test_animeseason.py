import unittest

from api.abstract import AbstractAPI
from api.animeseason import AnimeSeason
from core.log import Log


class AnimeseasonTest(unittest.TestCase):
    def setUp(self):
        AbstractAPI.CACHE['http://www.animeseason.com/anime-list/'] = open(
            "../cache/animeseason.anime-list.html").read()
        AbstractAPI.CACHE['http://www.animeseason.com/gosick/'] = open("../cache/animeseason.gosick.html").read()

        self.api = AnimeSeason()
        self.log = Log.create_log(__name__)

    def test_anime_list(self):
        # there should be 909 anime titles
        self.assertEqual(len(self.api.titles()), 909)

        # there should be 3 titles matching "clannad"
        titles = self.api.titles("clannad")
        self.assertEqual(len(titles), 3)

    def test_anime_information(self):
        titles = self.api.titles("clannad")
        self.log.info(titles)
        self.log.info(self.api.anime(titles[0][1]))
        self.log.info(self.api.recommendations(titles[0][1])[0])

    def test_title_search(self):
        titles = self.api.titles("clannad movie")
        self.assertEqual(len(titles), 1)