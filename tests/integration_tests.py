import unittest
from api import API
from api.aniDB import AniDB
from api.animeseason import AnimeSeason


class IntegrationTests(unittest.TestCase):
    @staticmethod
    def setUpClass():
        API.CACHE['http://myanimelist.net/anime/2167/Clannad/userrecs'] = open(
            "../cache/mal.clannad_userrecs.html").read()
        API.CACHE['http://myanimelist.net/api/anime/search.xml?q=Clannad'] = open(
            "../cache/mal.search_clannad.html").read()
        API.CACHE['http://anidb.net/api/animetitles.xml.gz'] = open("../cache/anidb.anime-titles.xml").read()
        API.CACHE['http://www.animeseason.com/anime-list/'] = open("../cache/animeseason.anime-list.html").read()
        API.CACHE['http://www.animeseason.com/gosick/'] = open("../cache/animeseason.gosick.html").read()


    def setUp(self):
        self.log = API.create_log(__name__)
        self.anidb = AniDB()
        self.animeseason = AnimeSeason()

    def test_animeseason_to_anidb_name_match(self):
        title = self.animeseason.search_title("clannad movie")
        self.log.info(self.anidb.search_title(title))