import MySQLdb


class Database():
    def __init__(self, **kwargs):
        self.connection = MySQLdb.connect(**kwargs)
        self.cursor = self.connection.cursor()
