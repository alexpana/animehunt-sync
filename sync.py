#!/usr/bin/env python

"""
sync.py
"""

from api.MAL import MyAnimeList
from api import API
from api.aniDB import AniDB
from api.animeseason import AnimeSeason

# Cache a few pages
API.CACHE['http://myanimelist.net/anime/2167/Clannad/userrecs'] = open("cache/mal.clannad_userrecs.html").read()
API.CACHE['http://myanimelist.net/api/anime/search.xml?q=Clannad'] = open("cache/mal.search_clannad.html").read()
API.CACHE['http://anidb.net/api/animetitles.xml.gz'] = open("cache/anidb.anime-titles.xml").read()
API.CACHE['http://www.animeseason.com/anime-list/'] = open("cache/animeseason.anime-list.html").read()
API.CACHE['http://www.animeseason.com/gosick/'] = open("cache/animeseason.gosick.html").read()
# Create a log
log = API.create_log("sync")

animeseason = AnimeSeason()
log.info(animeseason.anime("gosick"))