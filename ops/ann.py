import api
from core.log import Log


class AnimeNewsNetworkOperations:
    def __init__(self, db):
        self.db = db
        self.api = api.AnimeNewsNetwork()
        self.log = Log.create_log(__name__)

    def sync_new_titles(self):
        self.db.cursor.execute("SELECT ann_id FROM titles_ann")
        db_ids = map(lambda x: x[0], self.db.cursor.fetchall())
        api_ids = map(lambda x: x[0], self.api.titles())

        new_ids = set(api_ids).difference(set(db_ids))

        matches = []
        for ann_id in new_ids:
            try:
                api_anime = self.api.anime(id=ann_id)
                db_anime = self.db.find_anime({'title': api_anime['title'], 'synonyms': api_anime['synonyms']})
                animehunt_id = -1 if db_anime is None else db_anime['id']

                # Add the anime in the conversion table
                self.db.cursor.execute(
                    "INSERT INTO titles_ann (animehunt_id, ann_id) VALUES (%s, %s)" % (animehunt_id, ann_id))
                self.db.connection.commit()

                if db_anime is not None:
                    self.db.merge_synonyms(db_anime['id'], api_anime['synonyms'])
            except:
                self.log.info("Something went wrong trying to sync anime with id %d" % ann_id)

    def sync_unmatched_titles(self):
        self.db.cursor.execute("SELECT ann_id FROM titles_ann WHERE animehunt_id = -1")
        unmatched_ids = map(lambda x: x[0], self.db.cursor.fetchall())

        for ann_id in unmatched_ids:
            try:
                api_anime = self.api.anime(id=ann_id)
                db_anime = self.db.find_anime({'title': api_anime['title'], 'synonyms': api_anime['synonyms']})
                animehunt_id = -1 if db_anime is None else db_anime['id']

                if db_anime is not None:
                    self.db.cursor.execute(
                        "UPDATE titles_ann SET animehunt_id = %d WHERE ann_id = %d" % (animehunt_id, ann_id))
                    self.db.connection.commit()
                    self.db.merge_synonyms(db_anime['id'], api_anime['synonyms'])
            except:
                self.log.info("Something went wrong trying to sync anime with id %d" % ann_id)
