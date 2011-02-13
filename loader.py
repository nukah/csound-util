from celery.loaders.base import BaseLoader
from celery.datastructures import DictAttribute
from conf import RegistryError, conf
from logging import getLogger

class NodeLoader(BaseLoader):
    def __init__(self, *args, **kwargs):
        self._conf = {}
        log = getLogger(__name__)
        super(NodeLoader, self).__init__(*args, **kwargs)
        try:
            configuration = conf()
            self._conf = DictAttribute(configuration.getdict('CELERY'))
        except RegistryError, e:
            log.error(e)

    def on_worker_init(self):
        self.import_default_modules()

    @property
    def conf(self):
        return self._conf
