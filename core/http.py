class Http:
    def __init__(self):
        pass

        #@staticmethod
        #def request(url, auth=None):
        #    """
        #    Makes a HTTP request if required and caches the response.
        #    """
        #    url = url.replace(' ', '%20')
        #    self.log.debug("Requesting %s", url)
        #    if not url in AbstractAPI.CACHE:
        #        self.log.debug("Request sent to the server.")
        #        response = requests.get(url, auth=auth)
        #        if response.status_code == 200:
        #            AbstractAPI.CACHE[url] = response.content
        #        else:
        #            return ""
        #    else:
        #        pass
        #        self.log.debug("Cached response was found.")
        #    return AbstractAPI.CACHE[url]