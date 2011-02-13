from celery import app
from celery.app.defaults import DEFAULTS
from celery.utils import cached_property, import_from_cwd, get_cls_by_name
from celery.datastructures import ConfigurationView
from logging import getLogger
from copy import deepcopy
from conf import conf, RegistryError

class Node(app.App):
    def _config(self):
        log = getLogger(__name__)
        try:
            configuration = conf()
            self._conf = configuration.getdict('CELERY')
        except RegistryError, e:
            log.error(e)
        return ConfigurationView({},
                [self.prepare_config(self._conf), deepcopy(DEFAULTS)])
    @cached_property
    def conf(self):
        return self._config()
    @cached_property
    def loader(self):
        return get_cls_by_name('loader.NodeLoader', imp = import_from_cwd)(app = self)