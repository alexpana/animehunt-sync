from api import API
from api.aniDB import AniDB
from api.animeseason import AnimeSeason

__author__ = 'Alex'

import MySQLdb


class Database():
    def __init__(self, **kwargs):
        self.connection = MySQLdb.connect(**kwargs)
        self.cursor = self.connection.cursor()

    def search_title(self, title):
        self.cursor.execute("SELECT title FROM anime WHERE title LIKE '%%%s%%'" % title)
        return map(lambda x: x[0], self.cursor.fetchall())

    def update_anime(self, anime):
        pass


class Operations():
    def __init__(self, db_connection):
        self.db = db_connection
        self.api_animeseason = AnimeSeason()
        self.api_anidb = AniDB()
        self.log = API.create_log(__name__)

    def initialize_animeseason_titles(self):
        match_failures = 0

        for animeseason_title in self.api_animeseason.titles():
            anidb_title = self.api_anidb.search_title(animeseason_title)
            if anidb_title is None:
                match_failures += 1

            self.log.info("Inserting %s as %s into database" % (animeseason_title, anidb_title))
            try:
                self.db.cursor.execute(
                    "INSERT INTO animeseason_titles (animehunt, animeseason) VALUES (-1, '%s')" % animeseason_title)

                if anidb_title is not None:
                    self.db.cursor.execute(
                        "UPDATE animeseason_titles SET animehunt=(SELECT id from anime where title='%s') where animeseason='%s'" % (
                            anidb_title, animeseason_title)
                    )

                self.db.connection.commit()
            except:
                self.log.warn("There was a problem inserting %s into the database.")

        return match_failures, len(self.api_animeseason.titles())