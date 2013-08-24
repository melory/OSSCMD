#coding=utf8
from oss_api import *
from oss_xml_handler import *

'''
Mock a file system for testing purpose
'''
class OssFS:
    def __init__(self, host, id="", key=""):
        self.buckets = []
        self.host = host
        self.oss = OssAPI(host, id, key)

    def put_bucket(self, bucketname,acl='private'):
        if bucketname in self.buckets:
             return False
        res = self.oss.put_bucket(bucketname,acl)        
        if (res.status / 100) == 2:
            self.buckets.append(bucketname)
            return True
        else:
            return False

    def delete_bucket(self, bucketname):
        res = self.oss.delete_bucket(bucketname)
        if (res.status / 100) == 2:
            while bucketname in self.buckets:
                 del self.buckets[self.buckets.index(bucketname)]
                 return True
        else:
            return False

    def list_bucket(self):
        res = self.oss.get_service()
        if (res.status / 100) == 2:
            body = res.read()
            h = GetServiceXml(body)
            self.buckets = h.list()
        return self.buckets

    def get_bucket_acl(self, bucket):
        res = self.oss.get_bucket_acl(bucket)
        body = res.read()
        h = GetBucketAclXml(body)
        return h.grant


    def put_bucket_acl(self, bucket, acl=''):
        res = self.oss.put_bucket_acl(bucket,acl)
        if (res.status / 100) == 2:
            return True
        else:
            return False

    #fileobj is django defined uploaded file structure
    def upload_file(self, bucket, object, filename):
        res = self.oss.put_object_from_file(bucket, object, filename)
        if (res.status / 100) == 2:
            return True
        else:
            return False

    def make_dir(self, bucket, dirname):
        object = dirname + '/'
        res = self.oss.put_object_with_data(bucket, object, "")
        if (res.status / 100) == 2:
            return True
        else:
            return False

    def read_file(self, bucket, filename):
        res = self.oss.get_object(bucket, filename)
        return res.read()

    #return a list of file
    def list_file(self, bucket, prefix="", delim="", marker="", maxkeys=5):
        fl = []
        pl = []
        res = self.oss.get_bucket(bucket, prefix, delimiter=delim, marker=marker, maxkeys=maxkeys)
        if (res.status / 100) == 2:
            body = res.read()
            h = GetBucketXml(body)
            (fl, pl) = h.list()
        return (fl, pl)

    def delete_file(self, bucket, filename):
        res = self.oss.delete_object(bucket, filename)
        if (res.status / 100) == 2:
            return True
        else:
            return False

    def open_file_for_write(self, bucket, filename, filesize):
        conn = self.oss._open_conn_to_put_object(bucket, filename, filesize)
        return WriteFileObject(conn)

    def open_file_for_read(self, bucket, filename):
        res = self.oss.get_object(bucket, filename)
        return ReadFileObject(res)
            
class ReadFileObject:
    def __init__(self, res):
        self.res = res

    def read(self, buffer_size):
        if (self.res.status / 100) == 2:
            return self.res.read(buffer_size)
        else:
            return ""

    def close(self):
        if (self.res.status / 100) == 2:
            return True
        else:
            return False
        
class WriteFileObject:
    def __init__(self, conn):
        self.conn = conn

    def write(self, data):
        self.conn.send(data)
        
    def close(self):
        res = self.conn.getresponse()
        if (res.status / 100) == 2:
            return True
        else:
            return False

    
def test_open_file_for_write(bucket, object, filename):
    fp = file(filename, 'r')
    fp.seek(os.SEEK_SET, os.SEEK_END)
    filesize = fp.tell()
    fp.seek(os.SEEK_SET)
    wo = fs.open_file_for_write(bucket, object, filesize)
    l = fp.read(BufferSize)
    while len(l) > 0:
        print len(l)
        wo.write(l)
        l = fp.read(BufferSize)
    print wo.close()

def test_open_file_for_read(bucket, object, filename):
    fp = file(filename, 'w')
    ro = fs.open_file_for_read(bucket, object)
    buf = ro.read(1024)
    while len(buf) > 0:
        print len(buf)
        fp.write(buf)
        buf = ro.read(1024)
    print ro.close()

if __name__ == "__main__":
    host = '127.0.0.1:8080'
    id = ""
    key = ""
    BufferSize = 8000
    fs = OssFS(host, id, key)
    test_open_file_for_write('6uu', "a/b/c/d", "put.jpg")
    test_open_file_for_read('6uu', "a/b/c/d", "put.jpg")
    print fs.upload_file('6uu', "a/b/c", 'put.jpg')
    print fs.upload_file('6uu', "b/b/c", 'put.jpg')
    print fs.upload_file('6uu', "b/c", 'put.jpg')
    print fs.upload_file('6uu', "c", 'put.jpg')
    (fl, pl) = fs.list_file('bb1','',delim='',marker='')
    print fl
    print pl
    (fl, pl) = fs.list_file('bb1','',delim='',marker='')
    print fl
    print pl
