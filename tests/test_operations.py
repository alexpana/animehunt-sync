import time
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
        start_time = time.time()

        failed_matches, total_titles = self.operations.initialize_animeseason_titles()

        end_time = time.time()

        seconds = end_time - start_time

        self.log.info("Statistics and measurements")
        self.log.info("----------------------------------")
        self.log.info("Elapsed time: %dm%ds" % (seconds / 60, seconds % 60))
        self.log.info("Total titles: %d" % total_titles)
        self.log.info("Match speed: %.2f" % (float(total_titles) / float(end_time - start_time)))
        self.log.info("Failures: %d" % failed_matches)
        self.log.info("Failure percentage: %.2f" % (float(failed_matches) / float(total_titles) * 100))

        self.assertTrue(True)