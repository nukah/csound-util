from celery.loaders.base import BaseLoader
from celery.datastructures import DictAttribute
import logging

class NodeLoader(BaseLoader):
    def __init__(self, *args, **kwargs):
        self._conf = {}
        log = logging.get_logger(__name__)
        super(AppLoader, self).__init__(*args, **kwargs)
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
