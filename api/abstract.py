from cStringIO import StringIO
from lxml import etree
import requests
from api import Helper
from core.log import Log

__author__ = 'Alex'


class AbstractAPI:
    # internal cache for minimizing the number of outbound requests
    CACHE = {}

    def __init__(self, module):
        # Initialize the Logger object
        self.log = Log.create_log(module)

    def search(self, anime):
        """
        Searches for animes that fit match the anime mask
        (contain the same key,value pairs)
        """
        return []

    def anime(self, **kwargs):
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
            title_name = current_title[0]
            for synonym in [title_name] + self.synonyms(title_name):
                if Helper.canonic_matching(canonic_title, synonym):
                    matching_titles.append(current_title)
                if Helper.canonic_equals(canonic_title, synonym):
                    self.log.info("Found exact title: %s" % title_name)
                    return current_title

        if len(matching_titles) > 1:
            self.log.error("More than one anime was found and none matched the title perfectly.")
            self.log.error("Found titles: " + str(matching_titles))
        elif len(matching_titles) == 0:
            self.log.error("No anime was found with that name.")
        else:
            found_title = matching_titles[0]
            self.log.info("Found title by unique match: %s" % found_title)

        return found_title

    def titles(self, title=None):
        """
        Returns a list of all the titles provided by the API if title is None,
        else returns the list of titles that partially match the title parameter
        """
        return []

    def synonyms(self, title):
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
        if not url in AbstractAPI.CACHE:
            self.log.debug("Request sent to the server.")
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                AbstractAPI.CACHE[url] = response.content
            else:
                return ""
        else:
            pass
            self.log.debug("Cached response was found.")
        return AbstractAPI.CACHE[url]

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