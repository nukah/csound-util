from subprocess import Popen, PIPE
from celery.decorators import task 
from celery.task import Task
from celery.task.sets import subtask
import re, os, fcntl

QTypes = {"LQ" : "360",
          "SQ" : "480",
          "HQ" : "720"
          }

formats = {"4:3" : {"LD" : '-s 320x240 -qmin 14 -qmax 20', "SD" : '-s 640x480 -qmin 8 -qmax 15', "HD" : '-s 960x720 -qmin 6 -qmax 12'},
           "16:9" : {"LD" : '-s 640x360 -qmin 14 -qmax 20', "SD" : '-s 852x480 -qmin 8 -qmax 15', "HD" : '-s 1280x720 -qmin 6 -qmax 12'},
           }
#formats = {"4:3" : {"LD" : '-s 480x360 -b 650', "SD" : '-s 640x480 -b ', "HD" : '-s 960x720'},
#           "16:9" : {"LD" : '-s 640x360', "SD" : '-s 852x480', "HD" : '-s 1280x720'},
#           } 


FFMPEG = "ffmpeg"
SAVE_PATH = r"~/convert"

@task(name="analyze")
def analyze(name, path, aspect, height, callback = None, **kwargs):
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
        subtask(callback).delay(name, path, quality)

@task(name="convert")
def convert(name, path, quality, callback = None, **kwargs):
    log = Task.get_logger(**kwargs)
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
    process = Popen(options, shell=True, stderr=PIPE)
    finish_pattern = re.compile(r"\s\S+\s+(?P<video>\d+)\s\S+\s+(?P<audio>\d+)\s(?P<global headers>\d+)\s(?P<overhead>\d+)",re.X)
    ### todo functional objects: chunk read output
    #fcntl.fcntl(process.stderr.fileno(), fcntl.F_SETFL, fcntl.fcntl(process.stderr.fileno(), fcntl.F_GETFL) | os.O_NONBLOCK,)
    #pattern = re.compile("\S+\s+(?P<frame>\d+)
    #			\s\S+\s+(?P<fps>\d+)
    #			\sq=(?P<q>\S+)
    #			\s\S+\s+(?P<size>\S+)
    #			\stime=(?P<time>\S+)
    #			\sbitrate=(?P<bitrate>[\d\.]+)
    #			""", re.X)"
    
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
    
