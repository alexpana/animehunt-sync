import unittest
from api.helper import Helper

__author__ = 'Alex'


class HelperTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_canonic_matching(self):
        matching_titles = (
            ("clannad", "clannad the movie"),
            ("clannad movie", "clannad the movie"),
            ("Ergo!", "ergo proxy"),
            ("Ergo!", "proxy ergo"),
            ("clannad the movie", "clannad movie"))

        for match in matching_titles:
            self.assertTrue(Helper.canonic_matching(match[0], match[1]),
                            "'%s' did not match '%s' in canonic form" % (match[0], match[1]))

    def test_canonic_equals(self):
        titles = ("Clannad: The Movie", "Clannad Movie", "Clannad:  Movie")

        for i in range(len(titles) - 1):
            self.assertCanonicEqual(titles[i], titles[i + 1])

        self.assertNotCanonicEqual("Clannad", "Clannad Movie")

    def assertNotCanonicEqual(self, title1, title2):
        self.assertFalse(Helper.canonic_equals(title1, title2),
                         "'%s' was equal to '%s' in canonic form" % (title1, title2))

    def assertCanonicEqual(self, title1, title2):
        self.assertTrue(Helper.canonic_equals(title1, title2),
                        "'%s' was not equal to '%s' in canonic form" % (title1, title2))

