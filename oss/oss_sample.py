#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ossbrowser
## Author: melory
## Email:imsrch@melory.me
## License: GPL Version 2

import time
from oss_xml_handler import *
from oss_api import *

HOST="storage.aliyun.com"
ACCESS_ID = "YOUR ACCESS ID"
SECRET_ACCESS_KEY = "YOUR SECRET ACCESS KEY"
#ACCESS_ID and SECRET_ACCESS_KEY should not be empty, please input correct one.
   
if __name__ == "__main__": 
    #init oss,  get instance of oss
    if len(ACCESS_ID) == 0 or len(SECRET_ACCESS_KEY) == 0:
        print "Please make sure ACCESS_ID and SECRET_ACCESS_KEY are correct in ", __file__ , ", init are empty!"
        exit(0) 
    oss = OssAPI(HOST, ACCESS_ID, SECRET_ACCESS_KEY)
    sep = "=============================="
   
    #sign_url_auth_with_expire_time(self, method, url, headers = {}, resource="/", timeout = 60):
    method = "GET"
    bucket = "test" + time.strftime("%Y-%b-%d%H-%M-%S").lower()
    object = "test_object" 
    url = "http://" + HOST + "/oss/" + bucket + "/" + object
    headers = {}
    resource = "/" + bucket + "/" + object

    timeout = 60
    url_with_auth = oss.sign_url_auth_with_expire_time(method, url, headers, resource, timeout)
    print "after signature url is: ", url_with_auth
    print sep
    #put_bucket(self, bucket, acl='', headers = {}):
    acl = 'private'
    headers = {}
    res = oss.put_bucket(bucket, acl, headers)
    if (res.status / 100) == 2:
        print "put bucket ", bucket, "OK"
    else:
        print "put bucket ", bucket, "ERROR"
    print sep

    #get_service(self):
    res = oss.get_service()
    if (res.status / 100) == 2:
        body = res.read()
        h = GetServiceXml(body)
        print "bucket list size is: ", len(h.list())
        print "bucket list is: "
        for i in h.list():
            print i
    else:
        print res.status
    print sep

    #put_object_from_string(self, bucket, object, input_content, content_type=DefaultContentType, headers = {}):
    object = "object_test"
    input_content = "hello, OSS"
    content_type = "text/HTML"
    headers = {}
    res = oss.put_object_from_string(bucket, object, input_content, content_type, headers)
    if (res.status / 100) == 2:
        print "put_object_from_string OK"
    else:
        print "put_object_from_string ERROR"
    print sep
    
    #put_object_from_file(self, bucket, object, filename, content_type=DefaultContentType, headers = {}):
    object = "object_test"
    filename = __file__ 
    content_type = "text/HTML"
    headers = {}
    res = oss.put_object_from_file(bucket, object, filename, content_type, headers)
    if (res.status / 100) == 2:
        print "put_object_from_file OK"
    else:
        print "put_object_from_file ERROR"
    print sep
 
    #put_object_from_fp(self, bucket, object, fp, content_type=DefaultContentType, headers = {}):
    object = "object_test"
    filename = __file__
    content_type = "text/HTML"
    headers = {}

    fp = open(filename, 'rb')
    res = oss.put_object_from_fp(bucket, object, fp, content_type, headers)
    fp.close()
    if (res.status / 100) == 2:
        print "put_object_from_fp OK"
    else:
        print "put_object_from_fp ERROR"
    print sep

    #get_object(self, bucket, object, headers = {}):
    object = "object_test"
    headers = {}

    res = oss.get_object(bucket, object, headers)
    if (res.status / 100) == 2:
        print "get_object OK"
    else:
        print "get_object ERROR"
    print sep

    #get_object_to_file(self, bucket, object, filename, headers = {}):
    object = "object_test"
    headers = {}
    filename = "get_object_test_file"

    res = oss.get_object_to_file(bucket, object, filename, headers)
    if (res.status / 100) == 2:
        print "get_object_to_file OK"
    else:
        print "get_object_to_file ERROR"
    print sep

    #head_object(self, bucket, object, headers = {}):
    object = "object_test"
    headers = {}
    res = oss.head_object(bucket, object, headers)
    if (res.status / 100) == 2:
         print "head_object OK"
         header_map = convert_header2map(res.getheaders())
         content_len = safe_get_element("content-length", header_map)
         etag = safe_get_element("etag", header_map).upper()
         print "content length is:", content_len
         print "ETag is: ", etag

    else:
        print "head_object ERROR"
    print sep
    
    #get_bucket_acl(self, bucket):
    res = oss.get_bucket_acl(bucket)
    if (res.status / 100) == 2:
        body = res.read()
        h = GetBucketAclXml(body)
        print "bucket acl is:", h.grant 
    else:
        print "get bucket acl ERROR"
    print sep

    #get_bucket(self, bucket, prefix='', marker='', delimiter='', maxkeys='', headers = {}):
    prefix = ""
    marker = ""
    delimiter = "/"
    maxkeys = "100"
    headers = {}
    res = oss.get_bucket(bucket, prefix, marker, delimiter, maxkeys, headers)
    if (res.status / 100) == 2:
        body = res.read()
        h = GetBucketXml(body)
        (file_list, common_list) = h.list()
        print "object list is:"
        for i in file_list:
            print i
        print "common list is:"
        for i in common_list:
            print i
    print sep
 
    #upload_large_file(self, bucket, object, filename, thread_num = 10, max_part_num = 1000):
    res = oss.upload_large_file(bucket, object, __file__)    
    if (res.status / 100) == 2:
        print "upload_large_file OK"
    else:
        print "upload_large_file ERROR"

    print sep

    #get_object_group_index(self, bucket, object, headers = {})
    res = oss.get_object_group_index(bucket, object)
    if (res.status / 100) == 2:
        print "get_object_group_index OK"
        body = res.read()
        h = GetObjectGroupIndexXml(body)
        for i in h.list():
            print "object group part msg:", i
    else:
        print "get_object_group_index ERROR"

    res = oss.get_object_group_index(bucket, object)
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
                else:
                    print "delete part ", part_name, " in bucket:", bucket, " ok"
    print sep

    #delete_object(self, bucket, object, headers = {}):
    object = "object_test"
    headers = {}
    res = oss.delete_object(bucket, object, headers)
    if (res.status / 100) == 2:
        print "delete_object OK"
    else:
        print "delete_object ERROR"
    print sep

    #delete_bucket(self, bucket):
    res = oss.delete_bucket(bucket)
    if (res.status / 100) == 2:
        print "delete bucket ", bucket, "OK"
    else:
        print "delete bucket ", bucket, "ERROR"

    print sep


