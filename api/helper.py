__author__ = 'Alex'

import re


class Helper():
    _CACHE = {'canonic_forms': {}}

    def __init__(self):
        pass

    @staticmethod
    def canonic_form(title):
        if type(title) != str:
            return title
        if title not in Helper._CACHE['canonic_forms']:
            title = re.sub(r"[^a-zA-Z ]+", "", title).lower()
            value = Helper._CACHE['canonic_forms'] = filter(lambda x: len(x) > 0 and x not in ('of', 'the'),
                                                            title.split(" "))
            return value
        return Helper._CACHE['canonic_forms']

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
