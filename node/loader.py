from celery.loaders.base import BaseLoader

BUILTIN = ['celery.task']
class NodeLoader(BaseLoader):
    def import_default_modules(self):
        imports = self.app.conf.get('CELERY_IMPORTS') or None
        imports = set(imports.split(',') + BUILTIN)
        return map(self.import_task_module, imports)
        
    def on_worker_init(self):
        self.import_default_modules()
