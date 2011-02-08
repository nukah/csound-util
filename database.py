from pymongo import Connection
from bson import ObjectId

class DB(object):
    def __init__(self):
        self.connection = Connection('192.168.1.5', 27017)
        self.db = self.connection['database']
        self.c = self.db['videos']

    @property
    def collection(self):
        return self.c
    def __del__(self):
        self.connection.disconnect()
