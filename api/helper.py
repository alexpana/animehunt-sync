__author__ = 'Alex'

import re


class Helper():
    def __init__(self):
        pass

    @staticmethod
    def canonic_form(title):
        title = re.sub(r"[^a-zA-Z]+", "", title).lower()
        words = filter(lambda x: len(x) > 0, title.split(" "))

    @staticmethod
    def canonic_equals(title1, title2):
        return set(title1) == set(title2)