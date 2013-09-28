#!/usr/bin/env python

"""
sync.py
"""

import sys

from actions import Database
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

search_name = "berserk"


def test_mal():
    mal = MyAnimeList(username=sys.argv[1], password=sys.argv[2])
    log.info(mal.titles("berserk"))
    title = mal.search_title("clannad")
    log.info(mal.url(title))
    log.info(mal.anime(title))
    log.info(mal.recommendations(title))


def test_animeseason():
    animeseason = AnimeSeason()
    log.info(animeseason.titles("berserk"))
    title = animeseason.titles("clannad")[0]
    log.info(animeseason.url(title))
    log.info(animeseason.anime(title))
    log.info(animeseason.recommendations(title))


def test_anidb():
    anidb = AniDB()
    title = anidb.search_title("berserk")
    log.info(anidb.synonyms(title))


def test_database():
    db = Database(user="root", passwd=sys.argv[3], db="animehunt")
    log.info(db.search_title("Clannad"))


test_mal()
test_animeseason()
test_anidb()
test_mal()
test_database()