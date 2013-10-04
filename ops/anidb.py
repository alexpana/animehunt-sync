from api.anidb import AniDB
from core import Log

__author__ = 'Alex'


class AniDBOperations:
    def __init__(self, db):
        self.api = AniDB()
        self.db = db
        self.log = Log.create_log(__name__)

    def truncate(self):
        self.db.cursor.execute("TRUNCATE anime")
        self.db.cursor.execute("TRUNCATE synonyms")
        self.db.connection.commit()

    def sync_titles(self):
        api_titles = self.api.titles()
        db_titles = []
        new_titles = []

        self.db.cursor.execute("SELECT title FROM anime")
        db_titles = map(lambda x: x[0], self.db.cursor.fetchall())

        new_titles = set(api_titles).difference(set(db_titles))
        self.log.info("Found %d new titles." % len(new_titles))

        if len(new_titles) > 0:
            self._add_new_titles(new_titles)

        self._sync_old_titles(db_titles)

        self.db.connection.commit()

    def sync_all_synonyms(self):
        self.db.cursor.execute("SELECT id, title FROM anime")
        db_titles = self.db.cursor.fetchall()

        for anime_id, title in db_titles:
            self.sync_synonyms(title, anime_id)

    def sync_synonyms(self, title, anime_id=None):

        self.log.info("Synchronizing synonyms for title %s." % title)

        # Try to find out the animes ID
        if anime_id is None:
            self.db.cursor.execute("SELECT id FROM anime WHERE title='%s'" % title)
            anime_id = self.db.cursor.fetchall()[0][0]
        if anime_id is None:
            self.log.debug("Could not synchronize synonyms for %s. Title was not found in the database." % title)

        # Clean the synonyms for this anime
        self.db.cursor.execute("DELETE FROM synonyms WHERE animehunt_id=%s" % anime_id)
        self.db.connection.commit()

        api_synonyms = self.api.anime(title)['all']

        # Attempt to insert the new synonyms into the DB
        for synonym in api_synonyms:
            try:
                self.db.cursor.execute(
                    "INSERT INTO synonyms (animehunt_id, title, type, lang) "
                    "VALUES (%s, %s, %s, %s)",
                    (anime_id, synonym['title'], synonym['type'], synonym['lang']))
                self.db.connection.commit()
            except Exception as e:
                self.log.debug(
                    "Failed to insert synonym %s of %s into the synonyms table." % (unicode(synonym), title))
                self.log.debug("Exception message: %s", e)

        self.db.connection.commit()

    def _insert_new_title(self, anime_id, title):
        self.db.cursor.execute(
            "INSERT INTO anime (id, title, type, status, summary, episode_count) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            (anime_id, title, -1, -1, "", -1))

        self.db.cursor.execute(
            "INSERT INTO titles_anidb (animehunt_id, anidb_id) "
            "VALUES (%s, %s)" % (anime_id, self.api.anime(title)['id'])
        )

        self.db.connection.commit()

    def _add_new_titles(self, new_titles):
        self.log("Attempting to add %d new titles to the database." % len(new_titles))
        for title in new_titles:
            self.log.info("Inserting title %s." % title)
            self.db.cursor.execute("SELECT MAX(id) FROM anime")
            result = self.db.cursor.fetchall()
            anime_id = 1 if result[0][0] is None else int(result[0][0]) + 1

            self._insert_new_title(anime_id, title)

            self.sync_synonyms(title, anime_id)

    def _sync_old_titles(self, old_titles):
        self.log.info("Attempting to synchronize title IDs.")
        self.db.cursor.execute("SELECT title, id FROM anime")
        db_titles = dict(self.db.cursor.fetchall())

        for title in old_titles:
            anime_id = db_titles[title]

            self.db.cursor.execute("SELECT COUNT(id) FROM titles_anidb WHERE animehunt_id=%s" % anime_id)
            if self.db.cursor.fetchall()[0][0] == 0:
                self.log.info("Fixing missing conversion entry for %s." % title)
                self.db.cursor.execute(
                    "INSERT INTO titles_anidb (animehunt_id, anidb_id)"
                    "VALUES (%s, %s)" % (anime_id, self.api.anime(title)['id']))