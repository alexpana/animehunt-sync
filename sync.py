#!/usr/bin/env python

"""
sync.py
"""
from api import API
from config import SETTINGS

from db.MySQL import Database
from ops.anidb import AniDBOperations

API.CACHE["http://anidb.net/api/animetitles.xml.gz"] = open("cache/anidb.anime-titles.xml").read()

ops = AniDBOperations(Database(**SETTINGS['db']))
#ops.truncate()
#ops.sync_titles()
#ops.sync_titles()

ops.sync_all_synonyms()