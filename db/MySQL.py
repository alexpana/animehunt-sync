import MySQLdb
from api.helper import Helper
from core import Log


class Database():
    def __init__(self, **kwargs):
        self.connection = MySQLdb.connect(**kwargs)
        self.cursor = self.connection.cursor()
        self.log = Log.create_log(__name__)

    def disconnect(self):
        self.connection.close()

    def find_anime(self, anime):
        if 'id' in anime:
            return self._find_anime_by_id(anime['id'])
        elif 'title' in anime:
            return self._find_anime_by_title(anime['title'])

    def merge_anime(self, anime):
        if 'id' in anime.keys():
            self._update_anime(anime)
        else:
            self._insert_anime(anime)

    def get_anime_id(self, title):
        self.cursor.execute("SELECT animehunt_id FROM synonyms WHERE title = \"%s\"" % title)
        return self.cursor.fetchall()[0][0]

    def generate_unique_id(self):
        self.cursor.execute("SELECT MAX(id) FROM anime")
        result = self.cursor.fetchall()
        anime_id = 1 if result[0][0] is None else int(result[0][0]) + 1
        return anime_id

    def _insert_anime(self, anime):
        """
        Inserts a new anime in to the database.
        """
        if 'title' not in anime:
            self.log.info("Attempting to insert an anime with no title into the database.")
            return None

        anime = self._create_anime_record(anime, generate_id=True)
        try:
            self.cursor.execute(
                "INSERT INTO anime (id, title, type, status, summary, episode_count) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (anime['id'], anime['title'], anime['type'], anime['status'], anime['summary'], anime['episode_count']))
            self.connection.commit()
        except Exception as e:
            self.log.debug("Transaction failed. Exception: %s" % e)
            return None

        return anime

    def _update_anime(self, anime):
        raise NotImplementedError("Anime updating is not implemented yet.")

    def _find_anime_by_id(self, id):
        self.cursor.execute("SELECT id, title FROM anime WHERE id=%s", id)
        result = self.cursor.fetchone()
        return {'id': result[0], 'title': result[1]}

    def _find_anime_by_title(self, title):
        self.log.info("Searching for anime '%s' in the database." % title)
        canonic_sql_form = '%' + '%'.join(Helper.canonic_form(title)) + '%'
        self.cursor.execute("SELECT title FROM synonyms WHERE title LIKE '%s'" % canonic_sql_form)
        synonyms = map(lambda x: x[0], self.cursor.fetchall())
        canonic_matches = filter(lambda x: Helper.canonic_matching(title, x), synonyms)
        canonic_exact_matches = filter(lambda x: Helper.canonic_equals(title, x), canonic_matches)
        exact_matches = filter(lambda x: x.lower() == title.lower(), canonic_exact_matches)

        if len(exact_matches) == 1:
            return {'id': self.get_anime_id(exact_matches[0]), 'title': exact_matches[0]}

        if len(canonic_exact_matches) == 1:
            return {'id': self.get_anime_id(canonic_exact_matches[0]), 'title': canonic_exact_matches[0]}

        if len(canonic_exact_matches) > 1:
            sql_match_list = "(" + ", ".join(map(lambda x: "\"%s\"" % x, canonic_exact_matches)) + ")"
            self.cursor.execute("SELECT id, title FROM anime "
                                "WHERE id = (SELECT animehunt_id FROM synonyms WHERE title in %s)" % sql_match_list)
            result = self.cursor.fetchone()
            if result is not None:
                return {'id': result[0], 'title': result[1]}
            else:
                self.log.info("More than one anime was found with that name. Found ids are: %s", str(ids))
                return None

        self.log.info("No anime was found with that name in the database.")
        return None

    def _create_anime_record(self, anime, **kwargs):
        """
        Returns an anime dictionary with all it's required keys present
        """
        keys = ['id', 'title', 'type', 'status', 'summary', 'episode_count']
        default_values = {'type': None, 'status': None, 'summary': None, 'episode_count': None}

        # remove unused keys
        for key in anime:
            if key not in keys:
                anime.pop(key)

        # ensure required keys are present
        for key, value in default_values.items():
            if key not in anime:
                anime[key] = value

        # generate a new ID
        if 'id' not in anime or 'generate_id' in kwargs and kwargs['generate_id']:
            anime['id'] = self.generate_unique_id()

        return anime