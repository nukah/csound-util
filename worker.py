from subprocess import Popen, PIPE
from celery.decorators import task 
from celery.task import Task
from celery.task.sets import subtask
from pymongo import Connection
from socket import gethostname
from datetime import datetime
import re, bson

QTypes = {"LQ" : "360",
          "SQ" : "480",
          "HQ" : "720"
          }

formats = {"4:3" : {
                    "LD" : '-s 320x240 -qmin 16 -qmax 22', 
                    "SD" : '-s 640x480 -qmin 14 -qmax 18', 
                    "HD" : '-s 960x720 -qmin 5 -qmax 14'
                    },
           "16:9" : {
                     "LD" : '-s 640x360 -qmin 16 -qmax 22', 
                     "SD" : '-s 852x480 -qmin 12 -qmax 18', 
                     "HD" : '-s 1280x720 -qmin 5 -qmax 14'
                     },
           }

HOST = gethostname()
FFMPEG = "ffmpeg"
SAVE_PATH = r"~/convert"

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
        

@task(name="analyze")
def analyze(name, path, aspect, height, oid, callback = None, **kwargs):
    id = bson.ObjectId(oid=oid)
    height = height
    path = path
    name = "%s.%s" % (name, 'flv')
    quality = ""
    
    log = Task.get_logger(**kwargs)
    
    if aspect in formats.keys():
        if height < QTypes['LQ']:
            quality = formats[aspect]['LD']
        if height >= QTypes['LQ'] and height <= QTypes['SQ']:
            quality = formats[aspect]['SD']
        if height >= QTypes['SQ'] and height <= QTypes['HQ']:
            quality = formats[aspect]['HD']
        if height > QTypes['HQ']:
            quality = formats[aspect]['HD']
    else:
        asp_size = aspect.split(':')
        w = 640
        h = (w*asp_size[1])/asp_size[0]
        quality = '-s %dx%d' % (w,h)
    log.info("Starting analyze task with params %s [%s]" % (path, quality))
    
    if callback is not None:
        subtask(callback).delay(id, name, path, quality)

@task(name="convert", max_retries=2)
def convert(id, name, path, quality, callback = None, **kwargs):
    db = DB()
    log = Task.get_logger(**kwargs)
    finish_pattern = re.compile(r".*video:(?P<video>\d+)kB\s*audio:(?P<audio>\d+)kB\s*global\sheaders:(?P<headers>\d+)kB\s*muxing\soverhead\s(\d+\.?\d+)",re.X)
    task_id = kwargs['task_id']
     
    optdict = { 
                "FFMPEG" : FFMPEG,
                "INPUT_FILE" : path,
                "FORMAT" : "flv",
                "QUALITY" : quality,
                "ADDITIONAL_OPTS" : "-y",
                "FILEPATH" : '%s/%s' % (SAVE_PATH,name)
               }
    options = "{FFMPEG} -i {INPUT_FILE} -sn -f {FORMAT} {QUALITY} {ADDITIONAL_OPTS} {FILEPATH}".format(**optdict)
    
    log.info("Converting process for [%s] starting with params [%s]" % (name, optdict))
    db.collection.update({'_id' : id}, {'$set' : {'convert.host' : HOST}})
    process = Popen(options, shell=True, stderr=PIPE, close_fds=True) 
    output = process.stderr.read()
    match = finish_pattern.search(output)
    if not match:
        db.collection.update({'_id' : id }, {'$set' : {'converted' : 'False', 'convert.failed' : 'True', 'convert.last_retry' : datetime.now()}, '$inc' : {'convert.retries' : 1}})
        log.error("Converting process failed, retrying.")
    else:
        db.collection.update({'_id' : id }, {'$set' : {'converted' : 'True'}, '$unset' : { 'convert.failed' : 1, 'convert.retries' : 1, 'convert.last_retry' : 1}})
        log.info("Converting process finished successfully.")

    if callback is not None:
        subtask(callback).delay(path, name)
   
@task(name="thumbnails")
def thumbnails(path, name, **kwargs):
    log = Task.get_logger(**kwargs)
    optdict = { "FFMPEG" : FFMPEG,
                "INPUT_FILE" : path,
                "SIZE" : "200x200",
                "OUTPUT" : "%s\%s.%s.jpg" % (SAVE_PATH, name, "%d")
               }
    options = "{FFMPEG} -i {INPUT_FILE} -f image2 -r 0.1 -t 5 -vframes 4 -s {SIZE} {OUTPUT}".format(optdict)

### todo functional objects: chunk read output
#fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETFL, fcntl.fcntl(process.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,)
#pattern = re.compile("\S+\s+(?P<frame>\d+)
#            \s\S+\s+(?P<fps>\d+)
#            \sq=(?P<q>\S+)
#            \s\S+\s+(?P<size>\S+)
#            \stime=(?P<time>\S+)
#            \sbitrate=(?P<bitrate>[\d\.]+)
#            """, re.X)"
#       convert.retry([name, path, quality, callback], kwargs, countdown=60)

