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
    def __init__(self):
        pass