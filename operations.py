from api.aniDB import AniDB
from api.animeseason import AnimeSeason

__author__ = 'Alex'

import MySQLdb


class Database():
    def __init__(self, **kwargs):
        self.connection = MySQLdb.connect(**kwargs)
        self.cursor = self.connection.cursor()

    def search_title(self, title):
        self.cursor.execute("SELECT title from anime where title like '%%%s%%'" % title)
        return map(lambda x: x[0], self.cursor.fetchall())

    def update_anime(self, anime):
        pass


class Operations():
    def __init__(self, db_connection):
        self.connection = db_connection
        self.api_animeseason = AnimeSeason()
        self.api_anidb = AniDB()

    def sync_animeseason_titles(self):
        match_failures = 0
        for animeseason_title in self.api_animeseason.titles():
            anidb_title = self.api_anidb.search_title(animeseason_title)
            if anidb_title is None:
                match_failures += 1
        return match_failures, len(self.api_animeseason.titles())