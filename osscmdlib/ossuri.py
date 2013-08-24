import os
import re
import sys
from utils import unicodise

class OSSUri(object):
    type = None
    _subclasses = None

    def __new__(self, string):
        if not self._subclasses:
            ## Generate a list of all subclasses of OSSUri
            self._subclasses = []
            dict = sys.modules[__name__].__dict__
            for something in dict:
                if type(dict[something]) is not type(self):
                    continue
                if issubclass(dict[something], self) and dict[something] != self:
                    self._subclasses.append(dict[something])
        for subclass in self._subclasses:
            try:
                instance = object.__new__(subclass)
                instance.__init__(string)
                return instance
            except ValueError, e:
                continue
        raise ValueError("%s: not a recognized URI" % string)
    
    def __str__(self):
        return self.uri()

    def __unicode__(self):
        return self.uri()

    def public_url(self):
        raise ValueError("This OSS URI does not have Anonymous URL representation")

    def basename(self):
        return self.__unicode__().split(os.path.sep)[-1]

class OSSUriOSS(OSSUri):
    type = "oss"
    _re = re.compile("^oss://([^/]+)/?(.*)", re.IGNORECASE)
    def __init__(self, string):
        match = self._re.match(string)
        if not match:
            raise ValueError("%s: not a OSS URI" % string)
        groups = match.groups()
        self._bucket = groups[0]
        self._object = unicodise(groups[1])

    def bucket(self):
        return self._bucket

    def object(self):
        return self._object
    
    def has_bucket(self):
        return bool(self._bucket)

    def has_object(self):
        return bool(self._object)

    def uri(self):
        return "/".join(["oss:/", self._bucket, self._object])
    
    def public_url(self):
        return "http://storage.aliyun.com/%s/%s" % (self._bucket, self._object)

    def host_name(self):
        return "http://storage.aliyun.com/%s/" % (self._bucket)

    @staticmethod
    def compose_uri(bucket, object = ""):
        return "oss://%s/%s" % (bucket, object)

class OSSUriFile(OSSUri):
    type = "file"
    _re = re.compile("^(\w+://)?(.*)")
    def __init__(self, string):
        match = self._re.match(string)
        groups = match.groups()
        if groups[0] not in (None, "file://"):
            raise ValueError("%s: not a file:// URI" % string)
        self._path = unicodise(groups[1]).split(os.path.sep)

    def path(self):
        return os.path.sep.join(self._path)

    def uri(self):
        return os.path.sep.join([self.path()])

    def isdir(self):
        return os.path.isdir(self.path())

    def dirname(self):
        return os.path.dirname(self.path())

if __name__ == "__main__":
    uri = OSSUri("oss://bucket/object")
    print "type()  =", type(uri)
    print "uri     =", uri
    print "uri.type=", uri.type
    print "bucket  =", uri.bucket()
    print "object  =", uri.object()
    print

    uri = OSSUri("oss://bucket")
    print "type()  =", type(uri)
    print "uri     =", uri
    print "uri.type=", uri.type
    print "bucket  =", uri.bucket()
    print

    uri = OSSUri("/path/to/local/file.txt")
    print "type()  =", type(uri)
    print "uri     =", uri
    print "uri.type=", uri.type
    print "path    =", uri.path()
    print
    
