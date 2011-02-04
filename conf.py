import ConfigParser
import os, logging

__options__ = { 
               'CELERY' : ('CELERY_IMPORTS', 'CELERY_RESULT_BACKEND','CELERYD_LOG_FILE', 'CELERYD_LOG_LEVEL', 'BROKER_HOST', 'BROKER_PORT', 'BROKER_VHOST', 'BROKER_USER', 'BROKER_PASSWORD'),
               'AWS' : ('AWS_AUTH_KEY', 'AWS_SECRET_KEY', 'DEFAULT_SAVE_PATH', 'BUCKET_NAME'),
               'SYSTEM' : ()
               }

class RegistryError(Exception):
    pass

class conf(object):
    def __init__(self, config=None):
        self.log = logging.getLogger(__name__)
        self.config = os.path.join(os.getcwd(),"cfg.ini")
        if config is not None:
            self.config = os.path.isfile(config) and config
            
        try:
            cfg_file = open(self.config, 'r')
        except IOError:
            self.log.error("Can't read configuration file %s." % self.config)
        finally:
            cfg_file.close()
        
        self.conf = ConfigParser.SafeConfigParser()
        self.conf.optionxform = str
        self.conf.read(self.config)

        
        for section in __options__.keys():
            if self.conf.has_section(section):
                for option in __options__[section]:
                    if not self.conf.has_option(section, option):
                        self.log.error('Mandatory option %s in [%s] does not exist in config.' % (option, section))
                        raise RegistryError('Mandatory option %s in [%s] does not exist in config.' % (option, section))
            else:
                self.log.error('Mandatory section %s does not exist in config.' % section)
                raise RegistryError('Mandatory section %s does not exist in config.' % section)
    def __repr__(self):
        return str(map(lambda x: [x, self.conf.items(x)], self.conf.sections()))
            
    def __getattr__(self, section=None, option=None):
        if section and not option:
            return self.conf.options(section)
        return self.conf.get(section,option)
        