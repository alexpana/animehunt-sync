import unittest
from api.helper import Helper

__author__ = 'Alex'


class HelperTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_name_search(self):
        titles = ["Clannad: The Movie", "Clannad Movie", "Clannad:  Movie", "Clannad (Movie)", "Clannad (the Movie)"]
        canonic_titles = map(lambda x: Helper.canonic_form(x), titles)

        for i in range(len(titles) - 1):
            self.assertTrue(Helper.canonic_equals(canonic_titles[i], canonic_titles[i + 1]),
                            "%s was not equal to %s" % (canonic_titles[i], canonic_titles[i + 1]))