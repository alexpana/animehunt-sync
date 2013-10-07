__author__ = 'Alex'


class Helper():
    _CACHE = {'canonic_forms': {}}

    def __init__(self):
        pass

    @staticmethod
    def canonic_form(title):
        if type(title) not in (str, unicode):
            return title
        if title not in Helper._CACHE['canonic_forms']:
            processed_title = title.lower().replace("-", " ")
            clean_title = ""
            ignored_characters = "()[]/.!:?`'\"~"
            paren_count = 0
            for c in processed_title:
                if c == '(':
                    paren_count += 1
                if c == ')':
                    paren_count -= 1
                if paren_count == 0 and c not in ignored_characters or c.isdigit():
                    clean_title += c
            value = Helper._CACHE['canonic_forms'][title] = filter(
                lambda x: len(x) > 0 and x not in ('of', 'the', 'ova'),
                clean_title.split(" "))
            return value
        return Helper._CACHE['canonic_forms'][title]

    @staticmethod
    def canonic_equals(title1, title2):
        canonic_title1 = Helper.canonic_form(title1)
        canonic_title2 = Helper.canonic_form(title2)
        return canonic_title1 == canonic_title2

    @staticmethod
    def canonic_matching(title1, title2):
        canonic_title1 = set(Helper.canonic_form(title1))
        canonic_title2 = set(Helper.canonic_form(title2))
        return len(canonic_title1.difference(canonic_title2)) == 0
