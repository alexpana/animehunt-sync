from api.anidb import AniDB
from api.animeseason import AnimeSeason
from core.log import Log


class AnimeSeasonOperations:
    def __init__(self, db):
        self.log = Log.create_log(__name__)
        self.db = db
        self.api = AnimeSeason()

    def sync_titles(self):
        anidb = AniDB()
        self.sync_new_titles(anidb)
        self.sync_unmatched_titles()

    def sync_new_titles(self, anidb):
        new_titles = self._find_new_titles()
        self.log.info("Found %d new titles." % len(new_titles))

        for title in new_titles:
            self._match_and_sync(title, anidb)

    def sync_unmatched_titles(self):
        unmatched_titles = self._find_unmatched_titles()

        self.log.info("Found %d unmatched titles." % len(unmatched_titles))

        for title in unmatched_titles:
            animehunt_id = self.db.find_anime({'title': title})['id']
            if animehunt_id is not None:
                self.log.info("Found match for title %s." % title)
                self._update_title(title, animehunt_id)

    def sync_synonyms(self, title):
        # TODO: IMPLEMENT!
        pass

    def _find_unmatched_titles(self):
        self.db.cursor.execute("SELECT title FROM titles_animeseason WHERE animehunt_id = -1")
        unmatched_titles = map(lambda x: x[0], self.db.cursor.fetchall())
        return unmatched_titles

    def _find_new_titles(self):
        self.db.cursor.execute("SELECT title FROM titles_animeseason")
        db_titles = map(lambda x: x[0], self.db.cursor.fetchall())
        api_titles = self.api.titles()
        new_titles = set(api_titles).difference(set(db_titles))
        return new_titles

    def _match_and_sync(self, title, anidb):
        self.log.info("Attempting to match title %s against anidb." % title)
        anidb_title = anidb.search_title(title)
        if anidb_title is not None:
            self.log.info("Found match: %s. Attempting to match against database." % anidb_title)
            anidb_id = anidb.anime(anidb_title)['id']
            self.db.cursor.execute("SELECT animehunt_id FROM titles_anidb WHERE anidb_id=%s" % anidb_id)
            animehunt_id = self.db.cursor.fetchall()[0][0]

            self.db.cursor.execute("SELECT id FROM titles_animeseason WHERE title=\"%s\"" % title)
            entry_id = self.db.cursor.fetchall()[0][0]

            if entry_id is None:
                self._insert_title(animehunt_id, title)
            else:
                self._update_title(title, animehunt_id, entry_id)

        else:
            self.log.info("Failed to match %s." % title)

    def _insert_title(self, animehunt_id, title):
        try:
            self.db.cursor.execute(
                "INSERT INTO titles_animeseason (animehunt_id, title) "
                "VALUES (%s, \"%s\")" % (animehunt_id, title))
            self.db.connection.commit()
        except Exception as e:
            self.log.debug("Failed to insert %s into the database." % title)
            self.log.debug("Exception: %s" % e)

    def _update_title(self, title, animehunt_id, entry_id=None):
        if entry_id is None:
            self.db.cursor.execute("SELECT id FROM titles_animeseason WHERE title =\"%s\"" % title)
            entry_id = self.db.cursor.fetchall()[0][0]
        try:
            self.db.cursor.execute(
                "UPDATE titles_animeseason "
                "SET animehunt_id=%s, title=\"%s\" "
                "WHERE id=%s" % (animehunt_id, title, entry_id))
            self.db.connection.commit()
        except Exception as e:
            self.log.debug("Failed to insert %s into the database." % title)
            self.log.debug("Exception: %s" % e)
