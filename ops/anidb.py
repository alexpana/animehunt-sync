from api.anidb import AniDB
from core.log import Log

__author__ = 'Alex'


class AniDBOperations:
    def __init__(self, db):
        self.api = AniDB()
        self.db = db
        self.log = Log.create_log(__name__)

    def truncate(self):
        """
        Deletes every entry from the title conversion table
        """
        self.db.cursor.execute("TRUNCATE titles_anidb")
        self.db.connection.commit()

    def sync_titles(self):
        db_titles = self._database_titles()
        new_titles = self._find_new_titles()
        if len(new_titles) > 0:
            self.log.info("Found %d new titles." % len(new_titles))
            self._insert_titles(new_titles)
        else:
            self.log.info("No new titles found.")

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

        api_synonyms = self.api.anime(title=title)['all']

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

    def _database_titles(self):
        """
        Returns a list of all the titles in the database.
        """
        self.db.cursor.execute("SELECT title FROM anime")
        db_titles = map(lambda x: x[0], self.db.cursor.fetchall())
        return db_titles

    def _find_new_titles(self):
        """
        Returns a list of titles
        that are provided by the API
        but are not currently in the database.
        """
        self.db.cursor.execute("SELECT anidb_id FROM titles_anidb")
        db_indices = map(lambda x: int(x[0]), self.db.cursor.fetchall())

        api_indices = map(lambda x: int(self.api.anime(title=x)['id']), self.api.titles())
        new_indices = set(api_indices).difference(set(db_indices))

        # TODO: Finish this!
        #return filter(lambda x: x['id'] in new_indices, )

    def _insert_title(self, title):
        """
        Inserts a title in the database
        adding an entry to both 'anime'
        and 'titles_anidb'.
        """
        self.log.info("Inserting title %s." % title)

        # Add a new anime to the database with no additional information
        anime_id = self.db.merge_anime({'title': title})

        # Add a conversion entry in the titles_anidb table
        self.db.cursor.execute(
            "INSERT INTO titles_anidb (animehunt_id, anidb_id) "
            "VALUES (%s, %s)" % (anime_id, self.api.anime(title=title)['id'])
        )
        self.db.connection.commit()

        self.sync_synonyms(title, anime_id)

        return anime_id

    def _insert_titles(self, titles):
        self.log("Attempting to add %d titles to the database." % len(titles))
        for title in titles:
            self._insert_title(title)

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
                    "VALUES (%s, %s)" % (anime_id, self.api.anime(title=title)['id']))