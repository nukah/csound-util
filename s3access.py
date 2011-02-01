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
            self.create.set_acl(policy)

    @property
    def get(self):
        return self.connection.get_bucket(self.bucket)

class StoreObject(object):
    def __init__(self, id=None, file=None, bucket=None, policy=None):
        self.storage = Storage(bucket, policy).get
        self.key = Key(self.storage)
        self.key.key = id
        self.policy = policy or PUBLIC_POLICY
        if file and os.path.exists(os.path.abspath(file)):
            self.file = file
        else:
            StoringException('File not specified.')
            
    def send(self):
        if self.key.exists():
            raise StoringException('Key is already in use')
        else:
            self.key.set_contents_from_filename(self.file,policy=self.policy, cb=self.progress)
    
    def progress(self, part, complete):
        if part == complete:
            return True
        else:
            return False
    
    def __repr__(self):
        return self.key.__repr__()
    
    def delete(self):
        return self.key.delete()
        
    def set_meta(self, name, value):
        if name and value:
            self.key.set_metadata(name,value)
            
    @property 
    def url(self):
        pass
            
class GetObject(object):
    def __init__(self, id=None):
        self.storage = Storage().get
        self.kobj = Key(self.storage)
        self.kobj.key = id
                
    def get(self, path=DEFAULT_SAVE_PATH):
        if self.kobj.exists():
            self.filepath = os.path.join(path, self.kobj.key)
            self.kobj.get_contents_to_filename(self.filepath, cb=self.progress)
        else:
            raise StoringException('Key invalid.')
        
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

p = StoreObject('text1', 'c:\\bin\\libx264-medium.ffpreset')
p.send()