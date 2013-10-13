#!/usr/bin/env python

"""
sync.py
"""
import argparse

import api
import ops

from api.abstract import AbstractAPI
from config import SETTINGS
from core.log import Log
from db.mysql import Database


# Load the local cache into memory
AbstractAPI.CACHE["http://anidb.net/api/animetitles.xml.gz"] = open("cache/anidb.anime-titles.xml").read()
AbstractAPI.CACHE["http://www.animeseason.com/anime-list/"] = open("cache/animeseason.anime-list.html").read()
AbstractAPI.CACHE["http://myanimelist.net/malappinfo.php?u=coty9090&status=all&type=anime"] = \
    open("cache/mal.malappinfo.xml").read()
AbstractAPI.CACHE["http://www.animenewsnetwork.com/encyclopedia/reports.xml?id=155&nlist=all&type=anime"] = \
    open("cache/ann.reports.all.xml").read()

parser = argparse.ArgumentParser(description="Sync the animehunt database.")
#parser.add_argument('api', metavar='api', type=str, help="the api to use for the sync operation")
#parser.add_argument('--titles', dest='ops', type=str, const="all", default="all", help="a database sync operation")
#args = parser.parse_args()

log = Log.create_log("sync")
db = Database(**SETTINGS['db'])

api = {
    'as': api.AnimeSeason(),
    'mal': api.MyAnimeList(**SETTINGS['mal']),
    'anidb': api.AniDB(),
    'ann': api.AnimeNewsNetwork()}

ops = {
    'as': ops.AnimeSeasonOperations(db),
    'mal': ops.MALOperations(db, api['mal']),
    'anidb': ops.AniDBOperations(db),
    'ann': ops.AnimeNewsNetworkOperations(db)}
