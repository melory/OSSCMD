#coding=utf8
from oss_api import *
from oss_xml_handler import *

msg_remind = " PLEASE USE # TO SEPERATE EACH INPUT PARAMETER"

msg_quit = "q or quit, will quit out this console"
msg_help = "h or help, will show the message again"

#msg_get_service = "gs means get service , it lists all buckets that user has"
msg_get_service = "gs means get service."
example_get_service = "Input: gs"
GET_SERVICE = "get service"

#msg_put_bucket = "pb means put bucket, it creates bucket"
msg_put_bucket = "pb means put bucket."
example_put_bucket = "Input: pb#bucket||pb#bucket#acl||pb#bucket#acl#headers. "
PUT_BUCKET = "put bucket"

#msg_delete_bucket = "db means delete bucket, it deletes the bucket that user created"
msg_delete_bucket = "db means delete bucket."
example_delete_bucket = "Input: db#bucket"
DELETE_BUCKET = "delete bucket"

#msg_get_bucket = "gb means get bucket, it lists objects in the bucket"
msg_get_bucket = "gb means get bucket."
example_get_bucket = "Input: gb#bucket||gb#bucket#prefix||gb#bucket#prefix#marker||gb#bucket#prefix#marker#delimiter||gb#bucket#prefix#marker#delimiter#maxkeys||gb#bucket#prefix#marker#delimiter#maxkeys#headers"
GET_BUCKET = "get bucket"

#msg_get_bucket_acl = "gba means get bucket acl, it lists bucket acl"
msg_get_bucket_acl = "gba means get bucket acl."
example_get_bucket_acl = "Input: gba#bucket"
GET_BUCKET_ACL = "get bucket acl"

#msg_put_bucket_acl = "pba means put bucket acl, it sets bucket acl"
msg_put_bucket_acl = "pba means put bucket acl."
example_put_bucket_acl = "Input: pba#bucket#acl,  Example: pba#mybucket#public-read"
PUT_BUCKET_ACL = "put bucket acl"

#msg_put_object_with_data = "powd means put object with data, it puts object, its content from string data"
msg_put_object_with_data = "powd means put object with data."
example_put_object_with_data = "Input: powd#bucket#object#string_data||powd#bucket#object#string_data#content_type||powd#bucket#object#string_data#content_type#headers,  Example: powd#mybucket#myobjcet#abcdefghijk#txt/plain"
PUT_OBJECT_WITH_DATA = "put object with data"

#msg_put_object_from_file = "poff means put object from file, it puts object , its content from file"
msg_put_object_from_file = "poff means put object from file."
example_put_object_from_file = "Input: poff#bucket#object#filename||poff#bucket#object#filename#content_type||poff#bucket#object#filename#content_type#headers,  Example: poff#mybucket#myobjcet#myfilename"
PUT_OBJECT_FROM_FILE = "put object from file"

#msg_get_object = "go means get object, it gets object and print its content"
msg_get_object = "go means get object."
example_get_object = "Input: go#bucket#object||go#bucket#object#headers,  Example: go#mybucket#myobjcet"
GET_OBJECT = "get object"

#msg_get_object_to_file = "gotf means get object to file, it gets object and save its content to file"
msg_get_object_to_file = "gotf means get object to file."
example_get_object_to_file = "Input: gotf#bucket#object#filename||go#bucket#object#filename#headers,  Example: goff#mybucket#myobjcet#tofilename"
GET_OBJECT_TO_FILE = "get object to file"

#msg_delete_object = "do means delete object, it deletes object"
msg_delete_object = "do means delete object."
example_delete_object = "Input: do#bucket#object||do#bucket#object#headers,  Example: do#mybucket#myobjcet"
DELETE_OBJECT = "delete object"

#msg_head_object = "ho means head object, it gets meta info of object"
msg_head_object = "ho means head object."
example_head_object = "Input: ho#bucket#object||ho#bucket#object#headers,  Example: ho#mybucket#myobject"
HEAD_OBJECT = "head object"

def usage():
    width = 40
    print "=> 1) ", msg_quit.ljust(width)
    print "=> 2) ", msg_help.ljust(width)
    print '***************************************'
    print "NOTE:acl in below means access control level, acl SHOULD be public-read, private, or public-read-write"
    print "headers and parameters below means dic, it SHOULD be dic like a=b c=d"
    print "content type means object type , it is used in headers, default is application/octet-stream"
    print '***************************************'
    print 'bucket operation'
    print "=> 3) ", msg_get_service.ljust(width), example_get_service
    print "=> 4) ", msg_put_bucket.ljust(width), example_put_bucket
    print "=> 5) ", msg_delete_bucket.ljust(width), example_delete_bucket
    print "=> 6) ", msg_get_bucket.ljust(width), example_get_bucket
    print "=> 7) ", msg_get_bucket_acl.ljust(width), example_get_bucket_acl
    print "=> 8) ", msg_put_bucket_acl.ljust(width), example_put_bucket_acl
    print ''
    print '***************************************'
    print 'objcet operation'
    print "=> 9) ", msg_put_object_with_data.ljust(width), example_put_object_with_data
    print "=>10) ", msg_put_object_from_file.ljust(width), example_put_object_from_file
    print "=>11) ", msg_get_object.ljust(width), example_get_object
    print "=>12) ", msg_get_object_to_file.ljust(width), example_get_object_to_file
    print "=>13) ", msg_delete_object.ljust(width), example_delete_object
    print "=>14) ", msg_head_object.ljust(width), example_head_object
    print ''

def print_result(cmd, res):
    if res.status / 100 == 2:
        print cmd, "OK"
    else:
        print "error headers", res.getheaders()
        print "error body", res.read()
        print cmd, "Failed!"

def check_input(cmd_str, cmd_list, min, max):
    if len(cmd_list) < min or len(cmd_list) > max: 
        print "ERROR! ", cmd_str, "needs ", min, "-", max, " paramters"
        if example_map.has_key(cmd_str):
            print example_map[cmd_str]
        return False 
    else:
        return True

def get_cmd(cmd):
    string = cmd 
    tmp_list = string.split('#')
    cmd_list = []
    for i in tmp_list:
        if len(i.strip()) != 0:
            cmd_list.append(i.strip()) 
    return cmd_list
    
def transfer_string_to_dic(string):
    list = string.split() 
    dic = {} 
    for entry in list: 
        key, val = entry.split('=') 
        dic[key.strip()] = val.strip()
    print dic
    return dic

if __name__ == "__main__":
    import sys
    host = ""
    user_name = ""
    access_id = ""
    secret_access_key = ""
    remind = "the method you input is not supported! please input h or help to check method supported"
 
    if len(sys.argv) != 4:
        print '***************************************'
        print 'Please input the parameters like below'
        print '***************************************'
        print 'python ', __file__,' host access_id access_key'
        print 'host is the ip address with port of oss apache server . For Example: 10.249.105.22:8080'
        print 'access_id is public key that oss server provided. For Example: 84792jahfdsah+='
        print 'access_key is private secret key that oss server provided. For Example: atdh+=flahmzhha=+'
        print '***************************************'
        print ''
        print ''
        exit()
    else:
        host = sys.argv[1]
        access_id = sys.argv[2]
        secret_access_key = sys.argv[3]

    oss = OssAPI(host, access_id, secret_access_key)
    usage()
    bucketname = ""

    example_map = {}
    example_map[PUT_BUCKET] = example_put_bucket
    example_map[PUT_BUCKET_ACL] = example_put_bucket_acl
    example_map[GET_SERVICE] = example_get_service
    example_map[GET_BUCKET] = example_get_bucket
    example_map[DELETE_BUCKET] = example_delete_bucket
    example_map[GET_BUCKET_ACL] = example_get_bucket_acl
    example_map[PUT_OBJECT_WITH_DATA] = example_put_object_with_data
    example_map[PUT_OBJECT_FROM_FILE] = example_put_object_from_file
    example_map[GET_OBJECT] = example_get_object
    example_map[GET_OBJECT_TO_FILE] = example_get_object_to_file
    example_map[DELETE_OBJECT] = example_delete_object
    example_map[HEAD_OBJECT] = example_head_object
    
    while True:
        cmd = raw_input(">>")
        cmd = cmd.strip()
        cmd_list = get_cmd(cmd) 
        if ("q" == cmd.lower() or "quit" == cmd.lower()):
            break
        elif ("h" == cmd.lower() or "help" == cmd.lower()):
            usage()
        elif len(cmd_list) > 0:
            if cmd_list[0].lower() == "pb":
                cmd_str = PUT_BUCKET
                min = 2
                max = 4
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if len(cmd_list) == 2:
                        res = oss.put_bucket(cmd_list[1])
                    elif len(cmd_list) == 3:
                        res = oss.put_bucket(cmd_list[1], cmd_list[2])
                    elif len(cmd_list) == 4:
                        dic = transfer_string_to_dic(cmd_list[3])
                        res = oss.put_bucket(cmd_list[1], cmd_list[2], dic)
                    print_result(cmd_str, res)

            elif cmd_list[0] == "pba":
                cmd_str = PUT_BUCKET_ACL
                min = 3
                max = 3
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    res = oss.put_bucket(cmd_list[1], cmd_list[2])
                    print_result(cmd_str, res)

            elif cmd_list[0].lower() == "gs":
                cmd_str = GET_SERVICE
                min = 1
                max = 1
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    if len(cmd_list) == 1:
                        res = oss.get_service()
                    print_result(cmd_str, res)
                    if (res.status / 100) == 2:
                        body = res.read()
                        h = GetServiceXml(body)
                        print "bucket list size is: ", len(h.list())
                        print "bucket list is: "
                        for i in h.list():
                            print i

            elif cmd_list[0].lower() == "gb":
                cmd_str = GET_BUCKET
                min = 2
                max = 7
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    #get_bucket(bucket, prefix='', marker='', delimiter='', maxkeys='', headers = {}):
                    if len(cmd_list) == 2:
                        res = oss.get_bucket(cmd_list[1])
                    elif len(cmd_list) == 3:
                        res = oss.get_bucket(cmd_list[1], cmd_list[2])
                    elif len(cmd_list) == 4:
                        res = oss.get_bucket(cmd_list[1], cmd_list[2], cmd_list[3])
                    elif len(cmd_list) == 5:
                        res = oss.get_bucket(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4])
                    elif len(cmd_list) == 6:
                        res = oss.get_bucket(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4], cmd_list[5])
                    elif len(cmd_list) == 7:
                        dic = transfer_string_to_dic(cmd_list[6])
                        res = oss.get_bucket(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4], cmd_list[5], dic)
                    print_result(cmd_str, res)
                    if (res.status / 100) == 2:
                        body = res.read()
                        hh = GetBucketXml(body)
                        (fl, pl) = hh.list()
                        print "prefix list size is: ", len(pl)
                        print "prefix listis: "
                        for i in pl:
                            print i
                        print "file list size is: ", len(fl)
                        print "file list is: "
                        for i in fl:
                            print i

            elif cmd_list[0].lower() == "db":
                cmd_str = DELETE_BUCKET
                print cmd_str
                min = 2 
                max = 2
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    if len(cmd_list) == 2:
                        res = oss.delete_bucket(cmd_list[1])
                    print_result(cmd_str, res)

            elif cmd_list[0].lower() == "gba":
                cmd_str = GET_BUCKET_ACL
                print cmd_str
 
                min = 2
                max = 2
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if len(cmd_list) == 2:
                        res = oss.get_bucket_acl(cmd_list[1])
                    print_result(cmd_str, res)

                    if (res.status / 100) == 2:
                        body = res.read()
                        h = GetBucketAclXml(body)
                        print "bucket ", bucketname, " acl is: ", h.grant

            elif cmd_list[0].lower() == "powd" or cmd_list[0].lower() == "poff":
                if cmd_list[0].lower() == "powd":
                    cmd_str = PUT_OBJECT_WITH_DATA
                else:
                    cmd_str = PUT_OBJECT_FROM_FILE
                min = 4 
                max = 6
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if isinstance(cmd_list[2], str):
                        tmp = unicode(cmd_list[2], 'utf-8')
                        cmd_list[2] = tmp
                    if len(cmd_list) == 4:
                        if cmd_list[0].lower() == "powd":
                            res = oss.put_object_with_data(cmd_list[1], cmd_list[2], cmd_list[3])
                        else:
                            res = oss.put_object_from_file(cmd_list[1], cmd_list[2], cmd_list[3])
                    elif len(cmd_list) == 5:
                        if cmd_list[0].lower() == "powd":
                            res = oss.put_object_with_data(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4])
                        else:
                            res = oss.put_object_from_file(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4])
                    elif len(cmd_list) == 6:
                        if cmd_list[0].lower() == "powd":
                            dic = transfer_string_to_dic(cmd_list[5])
                            res = oss.put_object_with_data(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4], dic)
                        else:
                            dic = transfer_string_to_dic(cmd_list[5])
                            res = oss.put_object_from_file(cmd_list[1], cmd_list[2], cmd_list[3], cmd_list[4], dic)
                    print_result(cmd_str, res)

            elif cmd_list[0].lower() == "go":
                cmd_str = GET_OBJECT
                min = 3
                max = 4
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if len(cmd_list) == 3:
                        res = oss.get_object(cmd_list[1], cmd_list[2])
                    elif len(cmd_list) == 4:
                        dic = transfer_string_to_dic(cmd_list[3])
                        res = oss.get_object(cmd_list[1], cmd_list[2], dic)
                    print_result(cmd_str, res)
                    if res.status / 100 == 2:
                        print res.read()
 
            elif cmd_list[0].lower() == "gotf":
                cmd_str = GET_OBJECT_TO_FILE
                min = 4
                max = 5
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if len(cmd_list) == 4:
                        res = oss.get_object_to_file(cmd_list[1], cmd_list[2], cmd_list[3])
                    elif len(cmd_list) == 5:
                        dic = transfer_string_to_dic(cmd_list[4])
                        res = oss.get_object_to_file(cmd_list[1], cmd_list[2], cmd_list[3], dic)
                    print_result(cmd_str, res)
 
            elif cmd_list[0].lower() == "do":
                cmd_str = DELETE_OBJECT
                min = 3
                max = 4
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if len(cmd_list) == 3:
                        res = oss.delete_object(cmd_list[1], cmd_list[2])
                    elif len(cmd_list) == 4:
                        dic = transfer_string_to_dic(cmd_list[3])
                        res = oss.delete_object(cmd_list[1], cmd_list[2], dic)
                    print_result(cmd_str, res)

            elif cmd_list[0].lower() == "ho":
                cmd_str = HEAD_OBJECT
                min = 3
                max = 4
                if not check_input(cmd_str, cmd_list, min, max):
                    pass
                else:
                    print "cmd", cmd_list
                    bucketname = cmd_list[1]
                    if len(cmd_list) == 3:
                        res = oss.head_object(cmd_list[1], cmd_list[2])
                    elif len(cmd_list) == 4:
                        dic = transfer_string_to_dic(cmd_list[3])
                        res = oss.head_object(cmd_list[1], cmd_list[2], dic)
                    print_result(cmd_str, res)
                    if res.status / 100 == 2:
                        print res.getheaders()
            else:
                print remind
        else:
            print remind
