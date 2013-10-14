from core.log import Log


class MALOperations:
    def __init__(self, db, api):
        self.log = Log.create_log(__name__)
        self.db = db
        self.api = api

    def sync_new_titles(self):
        new_titles = self._find_new_titles()
        self.log.info("Found %d new titles." % len(new_titles))

        for title in new_titles:
            db_anime = self.db.find_anime({'title': title})
            mal_anime = self.api.experimental_anime(title)

            animehunt_id = -1 if db_anime is None else db_anime['id']
            mal_id = mal_anime['id']

            # Add the anime in the conversion table
            self.db.cursor.execute(
                "INSERT INTO titles_mal (animehunt_id, mal_id) VALUES (%s, %s)" % (animehunt_id, mal_id))
            self.db.connection.commit()

            if animehunt_id != -1:
                self.sync_synonyms(title)

    def sync_unmatched_titles(self):
        unmatched_titles = self._find_unmatched_titles_by_id()
        self.log.info("Found %d unmatched titles." % len(unmatched_titles))

        match_count = 0
        for anime_id in unmatched_titles:
            mal_anime = self.api.unofficial_anime(anime_id)
            mal_anime.pop('id')
            db_anime = self.db.find_anime(mal_anime)

            if db_anime is not None:
                self._match_anime(mal_anime, db_anime)
                self.log.info("Matched anime %s!" % mal_anime['title'])
                match_count += 1

        self.log.info("Matched %d animes." % len(match_count))

    def _match_anime(self, anime, db_anime):
        # update the conversion table
        self.db.cursor.execute(
            "UPDATE titles_mal SET animehunt_id = %d where mal_id = %d" % (db_anime['id'], anime['id']))
        self.db.connection.commit()
        self.db.merge_synonyms(db_anime['id'], anime['synonyms'], 4)

    def force_add_hentai(self):
        unmatched_titles = self._find_unmatched_titles_by_id()
        anime_count = 0
        for title_id in unmatched_titles:
            anime = self.api.unofficial_anime(title_id)
            if 'Hentai' in anime['genres']:
                anime_count += 1
                db_anime = self.db.insert_anime(anime)

                self._match_anime(anime, db_anime)

                self.log.info("Added hentai %s to the database." % anime['title'])

    def sync_synonyms(self, title):
        mal_anime = self.api.experimental_anime(title)

        # check that the anime is present in the conversion table
        results = self.cursor.execute("SELECT animehunt_id FROM titles_mal WHERE mal_id = %s" % mal_anime['id'])
        if results == 0:
            self.log.info("The anime was not found in the database. Please insert it first.")
            return
        animehunt_id = self.cursor.fetchone()[0]
        if animehunt_id == -1:
            self.log.info("The anime was found but not synced. Cannot add synonyms for unsynced animes.")
            return

        self.db.merge_synonyms(animehunt_id, mal_anime['synonyms'], 4)

    def _convert_ids_to_titles(self, ids):
        titles = []
        for title in self.api.experimental_titles():
            if self.api.experimental_anime(title)['id'] in ids:
                titles.append(title)
        return titles

    def _find_new_titles(self):
        api_ids = self.api.experimental_ids()

        self.db.cursor.execute("SELECT mal_id FROM titles_mal")
        db_ids = map(lambda x: x[0], self.db.cursor.fetchall())

        new_ids = set(api_ids).difference(set(db_ids))
        new_titles = self._convert_ids_to_titles(new_ids)
        return new_titles

    def _find_unmatched_titles_by_id(self):
        self.db.cursor.execute("SELECT mal_id FROM titles_mal WHERE animehunt_id = -1")
        return map(lambda x: x[0], self.db.cursor.fetchall())

    def _insert_title(self, title):
        pass
