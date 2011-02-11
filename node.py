from celery import app
from celery.utils import get_cls_by_name, import_from_cwd, cached_property

class Node(app.App):
    @cached_property
    def loader(self):
        return get_cls_by_name('loader.NodeLoader', imp = import_from_cwd)(app = self)
