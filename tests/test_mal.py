import unittest
from api.abstract import AbstractAPI
from api.mal import MyAnimeList
from config import SETTINGS
from core.log import Log


class MyAnimeListTest(unittest.TestCase):
    @staticmethod
    def setUpClass():
        AbstractAPI.CACHE['http://myanimelist.net/anime/2167/Clannad/userrecs'] = open(
            "../cache/mal.clannad_userrecs.html").read()
        AbstractAPI.CACHE['http://myanimelist.net/api/anime/search.xml?q=Clannad'] = open(
            "../cache/mal.search_clannad.html").read()
        AbstractAPI.CACHE["http://myanimelist.net/malappinfo.php?u=coty9090&status=all&type=anime"] = open(
            "../cache/mal.malappinfo.xml").read()

    def setUp(self):
        self.log = Log.create_log(__name__)
        self.api = MyAnimeList(**SETTINGS['mal'])

    def test_experimental_titles(self):
        titles = self.api.experimental_titles()
        ids = self.api.experimental_ids()
        self.assertEquals(type(titles), list)
        self.assertEquals(type(ids), list)
        self.assertEquals(len(titles), 8155)
        self.assertEquals(len(ids), 8155)
