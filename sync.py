#!/usr/bin/env python

"""
sync.py
"""

from api.MAL import MyAnimeList
from api import API
from api.aniDB import AniDB

# Cache a few pages
API.CACHE['http://myanimelist.net/anime/2167/Clannad/userrecs'] = open("cache/clannad_userrecs.html").read()
API.CACHE['http://myanimelist.net/api/anime/search.xml?q=Clannad'] = open("cache/search_clannad.html").read()
API.CACHE['http://anidb.net/api/animetitles.xml.gz'] = open("cache/anime-titles.xml").read()

# Create a log
log = API.create_log("sync")

mal_api = MyAnimeList(username='', password='')
#log.info("Clannad recommendations: %s", str(mal_api.recommendations("Clannad")))

anidb_api = AniDB()
titles = anidb_api.titles()

anime = mal_api.recommendations(titles[30][0])[0]
print anime

#log.info("All titles: %s", str(anidb_api.tiles()))