__author__ = 'Alex'

import re


class Helper():
    def __init__(self):
        pass

    @staticmethod
    def canonic_form(title):
        if type(title) == str:
            title = re.sub(r"[^a-zA-Z ]+", "", title).lower()
            return filter(lambda x: len(x) > 0 and x != 'the', title.split(" "))
        return title

    @staticmethod
    def canonic_equals(title1, title2):
        canonic_title1 = Helper.canonic_form(title1)
        canonic_title2 = Helper.canonic_form(title2)
        return set(canonic_title1) == set(canonic_title2)

    @staticmethod
    def canonic_matching(title1, title2):
        canonic_title1 = set(Helper.canonic_form(title1))
        canonic_title2 = set(Helper.canonic_form(title2))
        return len(canonic_title1.difference(canonic_title2)) == 0
