from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key
import os

AWS_AUTH_KEY = ""
AWS_SECRET_KEY = ""
DEFAULT_SAVE_PATH = "C:\\"
BUCKET_NAME = "csound"
PUBLIC_POLICY = "public-read"

class StoringException(Exception):
    pass

class Storage(object):
    def __init__(self, bucket=None, policy=None, location=None):
        self.connection = S3Connection(AWS_AUTH_KEY, AWS_SECRET_KEY)
        self.bucket = bucket or BUCKET_NAME
        self.policy = policy or PUBLIC_POLICY
        self.location = location or Location.EU
        if self.connection and not self.connection.get_bucket(self.bucket):
            self.create = self.connection.create_bucket(bucket, self.location)
            self.create.set_acl(self.policy)

    @property
    def instance(self):
        return self.connection.get_bucket(self.bucket)
    @property
    def name(self):
        return self.bucket


class StoreObject(object):
    def __init__(self, id=None, file=None, bucket=None, policy=None):
        self.connection = Storage(bucket, policy)
        self.storage = self.connection.instance
        self.bname = self.connection.name
        self.kobj = Key(self.storage)
        self.kobj.key = id
        self.policy = policy or PUBLIC_POLICY
        if file and os.path.exists(os.path.abspath(file)):
            self.file = file
        else:
            StoringException('File not specified.')
            
    def send(self):
        if self.kobj.exists():
            raise StoringException('Key <%s> is already in use' % self.kobj.key)
        else:
            self.kobj.set_contents_from_filename(self.file,policy=self.policy, cb=self.progress)
    
    def progress(self, part, complete):
        if part == complete:
            return True
        else:
            return False
    
    def __repr__(self):
        return self.kobj.__repr__()
    
    def delete(self):
        return self.kobj.delete()
        
    def set_meta(self, name, value):
        if name and value:
            self.kobj.set_metadata(name,value)
            
    @property 
    def url(self):
        return "http://s3.amazonaws.com/%s/%s" % (self.bname, self.kobj.key)
            
class GetObject(object):
    def __init__(self, id=None, bucket=None):
        self.connection = Storage(bucket)
        self.storage = self.connection.instance
        self.kobj = Key(self.storage)
        self.kobj.key = id
                
    def get(self, path=DEFAULT_SAVE_PATH):
        if self.kobj.exists():
            self.filepath = os.path.join(path, self.kobj.key)
            self.kobj.get_contents_to_filename(self.filepath, cb=self.progress)
        else:
            raise StoringException('Key <%s> invalid.' % self.kobj.key)
        
    def progress(self, part, complete):
        if part == complete:
            return True
        else:
            return False
            
    def delete(self):
        return self.kobj.delete()
    
    @property
    def path(self):
        return self.filepath