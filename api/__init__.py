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

    def _http_request(self, url, auth = None):
        """
        Makes a HTTP request if required and caches the response.
        """
        url = url.replace(' ', '%20')
        self.log.info("Requesting %s", url)
        if not url in API.CACHE:
            self.log.info("Request sent to the server.")
            response = requests.get(url, auth=auth)
            if response.status_code == 200:
                API.CACHE[url] = response.content
            else:
                return ""
        else:
            pass
            self.log.info("Cached response was found.")
        return API.CACHE[url]

    @staticmethod
    def create_log(module):
        log = logging.getLogger(module)
        log.setLevel(logging.DEBUG)
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
    def _parse_html(xml):
        """
        Returns an Element structure representing the root of the HTML
        """
        return etree.parse(StringIO(xml), etree.HTMLParser()).getroot()