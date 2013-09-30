import unittest2
from api import API
from operations import Operations


class TestOperations(unittest2.TestCase):

    @staticmethod
    def setUpClass():
        API.CACHE['http://anidb.net/api/animetitles.xml.gz'] = open("../cache/anidb.anime-titles.xml").read()
        API.CACHE['http://www.animeseason.com/anime-list/'] = open("../cache/animeseason.anime-list.html").read()

        TestOperations.operations = Operations(None)
        TestOperations.log = API.create_log(__name__)

    def test_animeseason_title_sync(self):
        self.log.info("Match failures: %d" % self.operations.sync_animeseason_titles())