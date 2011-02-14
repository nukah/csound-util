from pymongo import Connection
from bson import ObjectId
from logging import getLogger
from conf import conf, RegistryError

class DB(object):
    def __init__(self):
        log = getLogger(__name__)
        try:
            self.conf = conf().getdict("DATABASE")
        except RegistryError, e:
            log.error(e)
        host = self.conf.HOST or 'localhost'
        port = self.conf.PORT or 27017
        user = self.conf.USER
        password = self.conf.PASSWORD
        database = self.conf.DATABASE or 'sound'
        self.connection = Connection(host, port)
        self.db = self.connection[database].authenticate(user, password)
        self.c = self.db['videos']
    def get_oid(self, id):
        return ObjectId(id)

    @property
    def collection(self):
        return self.c
    def __del__(self):
        self.connection.disconnect()
