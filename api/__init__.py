from api.helper import Helper

__author__ = 'Alex'
import logging
import requests
import sys
from cStringIO import StringIO
from lxml import etree


class API:
    # internal cache for minimizing the number of outbound requests
    CACHE = {}

    def __init__(self, module):

        # Initialize the Logger object
        self.log = API.create_log(module)

    def anime(self, title):
        return {}

    def url(self, title):
        """
        Returns the url for the presentation page of the title
        """
        return ""

    def recommendations(self, title):
        return []

    def search_title(self, title):
        """
        Finds the *exact title* by matching the title parameter
        against all the titles provided by the API
        """
        self.log.info("Searching for titles matching %s" % title)

        canonic_title = Helper.canonic_form(title)
        self_titles = self.titles(title)
        matching_titles = []
        found_title = None

        for current_title in self_titles:
            canonic_titles_self = map(lambda x: Helper.canonic_form(x), [current_title] + self.synonyms(current_title))

            for canonic_synonym in canonic_titles_self:
                if Helper.canonic_matching(canonic_title, canonic_synonym):
                    matching_titles.append(current_title)
                if Helper.canonic_equals(canonic_title, canonic_synonym):
                    found_title = current_title

        if len(matching_titles) == 1 and found_title is None:
            found_title = matching_titles[0]

        if found_title is None:
            if len(matching_titles) > 1:
                self.log.error("More than one anime was found and none matched the title perfectly.")
                self.log.error("Found titles: " + str(matching_titles))
            else:
                self.log.error("No anime was found with that name.")
        else:
            self.log.info("Found title %s" % found_title)

        return found_title

    def titles(self, title=None):
        """
        Returns a list of all the titles provided by the API if title is None,
        else returns the list of titles that partially match the title parameter
        """
        return []

    def synonyms(self, title=None):
        """
        Returns a list of synonyms for the title
        """
        return []

    def _http_request(self, url, auth=None):
        """
        Makes a HTTP request if required and caches the response.
        """
        url = url.replace(' ', '%20')
        self.log.debug("Requesting %s", url)
        if not url in API.CACHE:
            self.log.debug("Request sent to the server.")
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                API.CACHE[url] = response.content
            else:
                return ""
        else:
            pass
            self.log.debug("Cached response was found.")
        return API.CACHE[url]

    @staticmethod
    def create_log(module):
        log = logging.getLogger(module)
        log.setLevel(logging.DEBUG)
        if len(log.handlers) == 0:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("[%(asctime)s] [%(name)s] %(message)s", "%H:%M:%S"))
            log.addHandler(handler)
        return log

    @staticmethod
    def _parse_xml(xml):
        """
        Returns an Element structure representing the root of the XML
        """
        return etree.fromstring(xml)

    @staticmethod
    def _parse_html(html):
        """
        Returns an Element structure representing the root of the HTML
        """
        return etree.parse(StringIO(html), etree.HTMLParser()).getroot()