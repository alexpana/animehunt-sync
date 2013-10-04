import unittest

from api import API
from api.anidb import AniDB
from core import Log


class AnimeseasonTest(unittest.TestCase):
    def setUp(self):
        API.CACHE["http://anidb.net/api/animetitles.xml.gz"] = open("../cache/anidb.anime-titles.xml").read()

        self.api = AniDB()
        self.log = Log.create_log(__name__)

    def test_anime_title_english(self):
        title = self.api.search_title("Zero no Tsukaima: Futatsuki no Kishi")
        self.log.info("Title found: %s" % title)
