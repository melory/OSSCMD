#coding=utf8
import urllib
import base64
import hmac
import time
from hashlib import sha1 as sha
import os
import md5
import StringIO
from oss_xml_handler import *
from threading import Thread

DEBUG = False 

self_define_header_prefix = "x-oss-"

class User:
    def __init__(self, user_name = "", access_id = "", secret_access_key = ""):
        self.user_name = user_name
        self.access_id = access_id
        self.secret_access_key = secret_access_key

    def show(self):
        print (('user_name:(%s) access_id:(%s) secret_access_key(%s)')) % (self.user_name,
                self.access_id, self.secret_access_key)


def _format_header(headers = {}):
    '''
    format the headers that self define
    convert the self define headers to lower.
    '''
    tmp_headers = {}
    for k in headers.keys():
        if k.lower().startswith(self_define_header_prefix):
            k_lower = k.lower()
            tmp_headers[k_lower] = headers[k]
        else:
            tmp_headers[k] = headers[k]
    return tmp_headers

def get_assign(secret_access_key, method, headers = {}, resource="/", result = []):
    '''
    Create the authorization for OSS based on header input.
    You should put it into "Authorization" parameter of header.
    '''
    content_md5 = ""
    content_type = ""
    date = ""
    canonicalized_oss_headers = ""
    if DEBUG:
        print "secret_access_key", secret_access_key
    content_md5 = safe_get_element('Content-Md5', headers)
    content_type = safe_get_element('Content-Type', headers)
    date = safe_get_element('Date', headers)
    canonicalized_resource = resource
    tmp_headers = _format_header(headers)
    if len(tmp_headers) > 0:
        x_header_list = tmp_headers.keys() 
        x_header_list.sort()
        for k in x_header_list: 
            if k.startswith(self_define_header_prefix):
                canonicalized_oss_headers += k + ":" + tmp_headers[k] + "\n"
    
    string_to_sign = method + "\n" + content_md5 + "\n" + content_type + "\n" + date + "\n" + canonicalized_oss_headers + canonicalized_resource;
    result.append(string_to_sign)
    if DEBUG:
        print "string_to_sign", string_to_sign, "string_to_sign_size", len(string_to_sign)
    
    h = hmac.new(secret_access_key, string_to_sign, sha)

    return base64.encodestring(h.digest()).strip()

def convert_header2map(header_list):
    header_map = {}
    for (a, b) in header_list:
        header_map[a] = b
    return header_map

def safe_get_element(name, container):
    if name in container:
        return container[name]
    else:
        return ""

def append_param(url, params):
    l = []
    for k,v in params.items():
        k = k.replace('_', '-')
        if  k == 'maxkeys':
            k = 'max-keys'
        if isinstance(v, unicode):
            v = v.encode('utf-8')
        if v is not None and v != '':
            l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        elif k == 'acl':
            l.append('%s' % (urllib.quote(k)))
    if len(l):
        url = url + '?' + '&'.join(l)
    return url

def create_object_group_msg_xml(part_msg_list = []):
    xml_string = r'<CreateFileGroup>'
    for part in part_msg_list:
        if len(part) >= 3:
            if isinstance(part[1], unicode):
                file_path = part[1].encode('utf-8')
            else:
                file_path = part[1]
            xml_string += r'<Part>'
            xml_string += r'<PartNumber>' + str(part[0]) + r'</PartNumber>'
            xml_string += r'<PartName>' + str(file_path) + r'</PartName>'
            xml_string += r'<ETag>"' + str(part[2]).upper() + r'"</ETag>'
            xml_string += r'</Part>'
        else:
            print "the ", part, " in part_msg_list is not as expected!"
            return ""
    xml_string += r'</CreateFileGroup>'

    return xml_string

def delete_all_parts_of_object_group(oss, bucket, object_group_name):
    res = oss.get_object_group_index(bucket, object_group_name)
    if res.status == 200:
        body = res.read()
        h = GetObjectGroupIndexXml(body)
        object_group_index = h.list()
        for i in object_group_index:
            if len(i) == 4 and len(i[1]) > 0:
                part_name = i[1].strip()
                res = oss.delete_object(bucket, part_name)
                if res.status != 204:
                    print "delete part ", part_name, " in bucket:", bucket, " failed!"
                    return False
                else:
                    print "delete part ", part_name, " in bucket:", bucket, " ok"
    else:
        return False

    return True;

def split_large_file(file_path, object_prefix = "", max_part_num = 1000, part_size = 10 * 1024 * 1024, buffer_size = 10 * 1024):
    parts_list = []

    if os.path.isfile(file_path):
        file_size = os.path.getsize(file_path)

        if file_size > part_size * max_part_num:
            part_size = (file_size + max_part_num - file_size % max_part_num) / max_part_num
        
        part_order = 1
        fp = open(file_path, 'rb')
        fp.seek(os.SEEK_SET)

        total_split_len = 0
        part_num = file_size / part_size
        if file_size % part_size != 0:
            part_num += 1

        for i in range(0, part_num):
            left_len = part_size
            real_part_size = 0 
            m = md5.new()
            offset = part_size * i
            while True:
                read_size = 0
                if left_len <= 0:
                    break
                elif left_len < buffer_size:
                    read_size = left_len
                else:
                    read_size = buffer_size

                buffer_content = fp.read(read_size)
                m.update(buffer_content)
                real_part_size += len(buffer_content)

                left_len = left_len - read_size 

            md5sum = m.hexdigest()

            temp_file_name = os.path.basename(file_path) + "_" + str(part_order)
            if len(object_prefix) == 0:
                file_name = sum_string(temp_file_name) + "_" + temp_file_name
            else:
                file_name = object_prefix + "/" + sum_string(temp_file_name) + "_" + temp_file_name
            part_msg = (part_order, file_name, md5sum, real_part_size, offset)
            total_split_len += real_part_size
            parts_list.append(part_msg)
            part_order += 1

        fp.close()
    else:
        print "ERROR! No file: ", file_path, ", please check."

    return parts_list

def sumfile(fobj):
    '''Returns an md5 hash for an object with read() method.'''
    m = md5.new()
    while True:
        d = fobj.read(8096)
        if not d:
            break
        m.update(d)
    return m.hexdigest()

def md5sum(fname):
    '''Returns an md5 hash for file fname, or stdin if fname is "-".'''
    if fname == '-':
        ret = sumfile(sys.stdin)
    else:
        try:
            f = file(fname, 'rb')
        except:
            return 'Failed to open file'
        ret = sumfile(f)
        f.close()
    return ret

def md5sum2(filename, offset = 0, partsize = 0):
    m = md5.new()
    fp = open(filename, 'rb')
    if offset > os.path.getsize(filename):
        fp.seek(os.SEEK_SET, os.SEEK_END)
    else:
        fp.seek(offset)

    left_len = partsize
    BufferSize = 8 * 1024
    while True:
        if left_len <= 0:
           break
        elif left_len < BufferSize:
           buffer_content = fp.read(left_len)
        else:
           buffer_content = fp.read(BufferSize)
        m.update(buffer_content)

        left_len = left_len - len(buffer_content) 
    md5sum = m.hexdigest() 
    return md5sum

def sum_string(content):
    f = StringIO.StringIO(content)
    md5sum = sumfile(f)
    f.close()
    return md5sum

class PutObjectGroupWorker(Thread):
    def __init__(self, oss, bucket, file_path, part_msg_list):
        Thread.__init__(self)
        self.oss = oss 
        self.bucket = bucket
        self.part_msg_list = part_msg_list
        self.file_path = file_path

    def run(self):
        for part in self.part_msg_list:
            if len(part) == 5:
                bucket = self.bucket
                file_name = part[1]
                object_name = file_name
                res = self.oss.head_object(bucket, object_name)
                if res.status == 200:
                    header_map = convert_header2map(res.getheaders())
                    etag = safe_get_element("etag", header_map)
                    md5 = part[2] 
                    if etag.replace('"', "").upper() == md5.upper():
                        continue

                partsize = part[3]
                offset = part[4]
                res = self.oss.put_object_from_file_given_pos(bucket, object_name, self.file_path, offset, partsize)
                if res.status != 200:
                    print "upload ", file_name, "failed!"," ret is:", res.status
                    print "headers", res.getheaders()      
            else:
                print "ERROR! part", part , " is not as expected!"

class GetAllObjects:
    def __init__(self):
        self.object_list = []

    def get_object_in_bucket(self, oss, bucket="", marker="", prefix=""):
        object_list = []
        res = oss.get_bucket(bucket, prefix, marker)
        body = res.read()
        hh = GetBucketXml(body)
        (fl, pl) = hh.list()
        if len(fl) != 0:
            for i in fl:
                if isinstance(i[0], unicode):
                    object = i[0].encode('utf-8')
                    object_list.append(object)

        if hh.is_truncated:
            marker = hh.nextmarker
        return (object_list, marker)


    def get_all_object_in_bucket(self, oss, bucket="", marker="", prefix=""):
        marker2 = ""
        while True:
            (object_list, marker) = self.get_object_in_bucket(oss, bucket, marker2, prefix)
            marker2 = marker
            if len(object_list) != 0:
                self.object_list.extend(object_list)

            if len(marker) == 0:
                break

def clear_all_objects_in_bucket(oss_instance, bucket):
    '''
    it will clean all objects in bucket, after that, it will delete this bucket.
    
    example:
    from oss_api import *
    host = ""
    id = ""
    key = ""
    oss_instance = OssAPI(host, id, key)
    bucket = "leopublicreadprivatewrite"
    if clear_all_objects_in_bucket(oss_instance, bucket):
        print "clean OK"
    else:
        print "clean Fail"
    '''
    b = GetAllObjects()
    b.get_all_object_in_bucket(oss_instance, bucket)
    for i in b.object_list:
        res = oss_instance.delete_object(bucket, i)
        if (res.status / 100 != 2):
            print "clear_all_objects_in_bucket: delete object fail, ret is:", res.status, "object is: ", i 
            return False
        else:
            print "clear_all_objects_in_bucket: delete object ok", "object is: ", i 
    res = oss_instance.delete_bucket(bucket)
    if (res.status / 100 != 2 and res.status != 404):
        print "clear_all_objects_in_bucket: delete bucket fail, ret is:", res.status
        return False
    return True

if __name__ == '__main__':
    pass
