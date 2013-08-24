#coding=utf8

# Copyright (c) 2011, Alibaba Cloud Computing 
# All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import httplib
import time
import base64
import hmac
import os
import urllib
import StringIO
from oss_util import *
from hashlib import sha1 as sha
        
class OssAPI:
    '''
    A simple OSS API 
    '''
    DefaultContentType = 'application/octet-stream'
    SendBufferSize = 8192
    GetBufferSize = 1024*1024*10

    def __init__(self, host, access_id, secret_access_key=""):
        self.host = host
        self.access_id = access_id
        self.secret_access_key = secret_access_key

    def sign_url_auth_with_expire_time(self, method, url, headers = {}, resource="/", timeout = 60):
        '''
        Create the authorization for OSS based on the input method, url, body and headers
        :type method: string
        :param method: one of PUT, GET, DELETE, HEAD 

        :type url: string 
        :param:HTTP address of bucket or object, eg: http://HOST/bucket/object

        :type headers: dict
        :param: HTTP header
        
        :type resource: string
        :param:path of bucket or object, eg: /bucket/ or /bucket/object 

        :type timeout: int
        :param

        Returns:
            signature url.
        '''

        send_time= safe_get_element('Date', headers)
        if len(send_time) == 0:
            send_time = str(int(time.time()) + timeout)
        headers['Date'] = send_time
        auth_value = get_assign(self.secret_access_key, method, headers, resource)
        params = {"OSSAccessKeyId":self.access_id, "Expires":str(send_time), "Signature":auth_value}
        return append_param(url, params)

    def _create_sign_for_normal_auth(self, method, headers = {}, resource="/"):
        '''
        NOT public API
        Create the authorization for OSS based on header input.
        it should be put into "Authorization" parameter of header.

        :type method: string
        :param:one of PUT, GET, DELETE, HEAD 
        
        :type headers: dict
        :param: HTTP header

        :type resource: string
        :param:path of bucket or object, eg: /bucket/ or /bucket/object

        Returns:
            signature string
        
        '''

        auth_value = "OSS " + self.access_id + ":" + get_assign(self.secret_access_key, method, headers, resource)
        return auth_value
       
    def bucket_operation(self, method, bucket, headers={}, params={}):
        '''
        Send bucket operation request 

        :type method: string
        :param method: one of PUT, GET, DELETE, HEAD

        :type bucket: string
        :param

        :type headers: dict
        :param: HTTP header

        :type params: dict
        :param: parameters that will be appeded at the end of resource 

        Returns:
            HTTP Response

        '''

        url = append_param("/" + bucket + "/", params)
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        # Create REST header
        headers['Date'] = date
        headers['Host'] = self.host
        if params.has_key('acl'):
            resource = "/" + bucket + "/?acl"
        else:
            resource = "/" + bucket + "/"
        if "" != self.secret_access_key and "" != self.access_id:
            headers['Authorization'] = self._create_sign_for_normal_auth(method, headers, resource) 
        elif "" != self.access_id:
            headers['Authorization'] = self.access_id 
            
        conn = httplib.HTTPConnection(self.host)
        conn.request(method, url, "", headers)
        return conn.getresponse()

    def object_operation(self, method, bucket, object, headers = {}, data=""):
        '''
        Send Object operation request
        
        :type method: string
        :param method: one of PUT, GET, DELETE, HEAD

        :type bucket: string
        :param
        
        :type object: string
        :param
        
        :type headers: dict
        :param: HTTP header

        :type data: string
        :param
        
        Returns:
            HTTP Response
        '''
        
        if isinstance(object, unicode):
            object = object.encode('utf-8')
        resource = "/" + bucket + "/"
        resource = resource.encode('utf-8') + object 
        object = urllib.quote(object)
        url = "/" + bucket + "/" + object
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

         # Create REST header
        headers['Date'] = date
        headers['Host'] = self.host
        if "" != self.secret_access_key and "" != self.access_id:
            headers['Authorization'] = self._create_sign_for_normal_auth(method, headers, resource) 
        elif "" != self.access_id:
            headers['Authorization'] = self.access_id 

        conn = httplib.HTTPConnection(self.host)
        conn.request(method, url, data, headers)
        return conn.getresponse()

    def get_service(self):
        '''
        List all buckets of user
        '''
        return self.list_all_my_buckets()

    def list_all_my_buckets(self):
        '''
        List all buckets of user
        '''

        method = "GET"
        url = "/"
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        headers = {}

        headers['Date'] = date
        headers['Host'] = self.host
        resource = "/"
        if "" != self.secret_access_key and "" != self.access_id:
            headers['Authorization'] = self._create_sign_for_normal_auth(method, headers, resource) 
        elif "" != self.access_id:
            headers['Authorization'] = self.access_id 
     
        conn = httplib.HTTPConnection(self.host)
        conn.request(method, url, "", headers)
        return conn.getresponse()

    def get_bucket_acl(self, bucket):
        '''
        Get Access Control Level of bucket
        
        :type bucket: string
        :param

        Returns:
            HTTP Response
        '''
        headers = {}
        params = {}
        params['acl'] = ''
        return self.bucket_operation("GET", bucket, headers, params)

    def get_bucket(self, bucket, prefix='', marker='', delimiter='', maxkeys='', headers = {}):
        '''
        List object that in bucket
        '''
        return self.list_bucket(bucket, prefix, marker, delimiter, maxkeys, headers)

    def list_bucket(self, bucket, prefix='', marker='', delimiter='', maxkeys='', headers = {}):
        '''
        List object that in bucket

        :type bucket: string
        :param

        :type prefix: string
        :param  
        
        :type marker: string
        :param
        
        :type delimiter: string
        :param
        
        :type maxkeys: string
        :param

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        params = {}
        params['prefix'] = prefix
        params['marker'] = marker
        params['delimiter'] = delimiter
        params['max-keys'] = maxkeys
        return self.bucket_operation("GET", bucket, headers, params)

    def create_bucket(self, bucket, acl='', headers = {}):
        '''
        Create bucket
        '''
        return self.put_bucket(bucket, acl, headers)

    def put_bucket(self, bucket, acl='', headers = {}):
        '''
        Create bucket
        
        :type bucket: string
        :param

        :type acl: string
        :param: one of private
        
        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        if acl != '':
            headers['x-oss-acl'] = acl
        return self.bucket_operation("PUT", bucket, headers)

    def delete_bucket(self, bucket):
        '''
        Delete bucket
        
        :type bucket: string
        :param
        
        Returns:
            HTTP Response
        '''

        return self.bucket_operation("DELETE", bucket)

    def put_object_with_data(self, bucket, object, input_content, content_type=DefaultContentType, headers = {}):
        '''
        Put object into bucket, the content of object is from input_content
        '''
        return self.put_object_from_string(bucket, object, input_content, content_type, headers)

    def put_object_from_string(self, bucket, object, input_content, content_type=DefaultContentType, headers = {}):
        '''
        Put object into bucket, the content of object is from input_content

        :type bucket: string
        :param
        
        :type object: string
        :param
        
        :type input_content: string
        :param

        :type content_type: string
        :param: the object content type that supported by HTTP

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        headers['Content-Type'] = content_type
        headers['Content-Length'] = str(len(input_content))
        fp = StringIO.StringIO(input_content)
        res = self.put_object_from_fp(bucket, object, fp, content_type, headers)
        fp.close()
        return res

    def _open_conn_to_put_object(self, bucket, object, filesize, content_type=DefaultContentType, headers = {}):
        '''
        NOT public API
        Open a connectioon to put object

        :type bucket: string
        :param

        :type filesize: int 
        :param
        
        :type object: string
        :param
        
        :type input_content: string
        :param

        :type content_type: string
        :param: the object content type that supported by HTTP

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        method = "PUT"
        if isinstance(object, unicode):
            object = object.encode('utf-8')
        resource = "/" + bucket + "/"
        resource = resource.encode('utf-8') + object 
        object = urllib.quote(object)
        url = "/" + bucket + "/" + object
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())

        conn = httplib.HTTPConnection(self.host)
        conn.putrequest(method, url)
        headers["Content-Type"] = content_type
        headers["Content-Length"] = filesize
        headers["Date"] = date
        headers["Host"] = self.host
        headers["Expect"] = "100-Continue"
        for k in headers.keys():
            conn.putheader(k, headers[k])
        if "" != self.secret_access_key and "" != self.access_id:
            auth = self._create_sign_for_normal_auth(method, headers, resource)
            conn.putheader("Authorization", auth)
        conn.endheaders()
        return conn

    def put_object_from_file(self, bucket, object, filename, content_type=DefaultContentType, headers = {}):
        '''
        put object into bucket, the content of object is read from file        

        :type bucket: string
        :param
        
        :type object: string
        :param
        
        :type fllename: string
        :param: the name of the read file 

        :type content_type: string
        :param: the object content type that supported by HTTP

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''
        fp = open(filename, 'rb')
        res = self.put_object_from_fp(bucket, object, fp, content_type, headers)
        fp.close()
        return res

    def put_object_from_fp(self, bucket, object, fp, content_type=DefaultContentType, headers = {}):
        '''
        Put object into bucket, the content of object is read from file pointer

        :type bucket: string
        :param
        
        :type object: string
        :param
        
        :type fp: file 
        :param: the pointer of the read file 

        :type content_type: string
        :param: the object content type that supported by HTTP

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''
        
        fp.seek(os.SEEK_SET, os.SEEK_END)
        filesize = fp.tell()
        fp.seek(os.SEEK_SET)

        conn = self._open_conn_to_put_object(bucket, object, filesize, content_type, headers)
        l = fp.read(self.SendBufferSize)
        while len(l) > 0:
            conn.send(l)
            l = fp.read(self.SendBufferSize)
        return conn.getresponse()

    def get_object(self, bucket, object, headers = {}):
        '''
        Get object

        :type bucket: string
        :param
        
        :type object: string
        :param

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        return self.object_operation("GET", bucket, object, headers)

    def get_object_to_file(self, bucket, object, filename, headers = {}):
        '''
        Get object and write the content of object into a file

        :type bucket: string
        :param
        
        :type object: string
        :param

        :type filename: string
        :param

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        res = self.get_object(bucket, object, headers)
        f = file(filename, 'wb')
        data = ""
        while True:
            data = res.read(self.GetBufferSize)
            if len(data) != 0:
                f.write(data)
            else:
                break
        f.close()
        # TODO: get object with flow
        return res

    def delete_object(self, bucket, object, headers = {}):
        '''
        Delete object
        
        :type bucket: string
        :param
        
        :type object: string
        :param

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        return self.object_operation("DELETE", bucket, object, headers)

    def head_object(self, bucket, object, headers = {}):
        '''
        Head object, to get the meta message of object without the content
        
        :type bucket: string
        :param
        
        :type object: string
        :param

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        return self.object_operation("HEAD", bucket, object, headers)

    def post_object_group(self, bucket, object, object_group_msg_xml, headers = {}, params = {}):
        '''
        Post object group, merge all objects in object_group_msg_xml into one object
        :type bucket: string
        :param

        :type object: string
        :param
        
        :type object_group_msg_xml: string
        :param: xml format string, like
                <CreateFileGroup>
                    <Part>
                        <PartNumber>N</PartNumber>
                        <FileName>objectN</FileName>
                        <Etag>"47BCE5C74F589F4867DBD57E9CA9F808"</Etag>
                    </Part>
                </CreateFileGroup>
        :type headers: dict
        :param: HTTP header

        :type params: dict
        :param: parameters
        
        Returns:
            HTTP Response
        '''
        method = "POST"
        url = "/" + bucket + "/" + object + "?group"
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        # Create REST header
        headers['Date'] = date
        headers['Host'] = self.host
        headers['Content-Type'] = 'text/xml'
        headers['Content-Length'] = len(object_group_msg_xml)
        resource = "/" + bucket + "/" + object + "?group"
        if "" != self.secret_access_key and "" != self.access_id:
            headers['Authorization'] = self._create_sign_for_normal_auth(method, headers, resource)
        elif "" != self.access_id:
            headers['Authorization'] = self.access_id 

        conn = httplib.HTTPConnection(self.host)
        conn.request(method, url, object_group_msg_xml, headers)
        return conn.getresponse()

    def get_object_group_index(self, bucket, object, headers = {}):
        '''
        Get object group_index 

        :type bucket: string
        :param
        
        :type object: string
        :param

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''

        headers["x-oss-file-group"] = ""
        return self.object_operation("GET", bucket, object, headers)


    def put_object_from_file_given_pos(self, bucket, object, filename, offset, partsize, content_type=DefaultContentType, headers = {}):
        '''
        Put object into bucket, the content of object is read from given posision of filename
        :type bucket: string
        :param
        
        :type object: string
        :param
        
        :type fllename: string
        :param: the name of the read file 
        
        :type offset: int
        :param: the given position of file

        :type partsize: int
        :param: the size of read content 
    
        :type content_type: string
        :param: the object content type that supported by HTTP

        :type headers: dict
        :param: HTTP header

        Returns:
            HTTP Response
        '''
        fp = open(filename, 'rb')
        if offset > os.path.getsize(filename):
            fp.seek(os.SEEK_SET, os.SEEK_END)
        else:
            fp.seek(offset)

        conn = self._open_conn_to_put_object(bucket, object, partsize, content_type, headers)

        left_len = partsize 
        while True:
            if left_len <= 0:
               break
            elif left_len < self.SendBufferSize:
               buffer_content = fp.read(left_len)
            else:
               buffer_content = fp.read(self.SendBufferSize)

            if len(buffer_content) > 0:
                conn.send(buffer_content)

            left_len = left_len - len(buffer_content)

        fp.close()
        return conn.getresponse()

    def upload_large_file(self, bucket, object, filename, thread_num = 10, max_part_num = 1000):
        '''
        Upload large file, the content is read from filename. The large file is splitted into many parts. It will        put the many parts into bucket and then merge all the parts into one object. 

        :type bucket: string
        :param
        
        :type object: string
        :param
        
        :type fllename: string
        :param: the name of the read file 
 
        '''
        #split the large file into 1000 parts or many parts
        #get part_msg_list
        if isinstance(filename, unicode):
            filename = filename.encode('utf-8')

        part_msg_list = split_large_file(filename, object, max_part_num)

        #make sure all the parts are put into same bucket
        if len(part_msg_list) < thread_num and len(part_msg_list) != 0:
            thread_num = len(part_msg_list)

        step = len(part_msg_list) / thread_num
        threadpool = []
        for i in range(0, thread_num):
            if i == thread_num - 1:
                end = len(part_msg_list)
            else:
                end = i * step + step

            begin = i * step
            oss = OssAPI(self.host, self.access_id, self.secret_access_key)
            current = PutObjectGroupWorker(oss, bucket, filename, part_msg_list[begin:end])
            threadpool.append(current)
            current.start()

        for item in threadpool:
            item.join()
       
        #get xml string that contains msg of object group
        object_group_msg_xml = create_object_group_msg_xml(part_msg_list)

        return self.post_object_group(bucket, object, object_group_msg_xml)
