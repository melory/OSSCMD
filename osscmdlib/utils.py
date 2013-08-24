#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ossbrowser
## Author: melory
## Email:imsrch@melory.me
## License: GPL Version 2

import os
import sys
import time
import re
import hmac
import base64

from logging import debug, info, warning, error

import Config

# hashlib backported to python 2.4 / 2.5 is not compatible with hmac!
if sys.version_info[0] == 2 and sys.version_info[1] < 6:
    from md5 import md5
    import sha as sha1
else:
    from hashlib import md5, sha1



__all__ = []

def formatSize(size, human_readable = False, floating_point = False):
    size = floating_point and float(size) or int(size)
    if human_readable:
        coeffs = ['k', 'M', 'G', 'T']
        coeff = ""
        while size > 2048:
            size /= 1024
            coeff = coeffs.pop(0)
        return (size, coeff)
    else:
        return (size, "")
__all__.append("formatSize")

def dateOSStoPython(date):
    date = re.compile("(\.\d*)?Z").sub(".000Z", date)
    return time.strptime(date, "%Y-%m-%dT%H:%M:%S.000Z")
__all__.append("dateOSStoPython")

def formatDateTime(osstimestamp):
    return time.strftime("%Y-%m-%d %H:%M", dateOSStoPython(osstimestamp))
__all__.append("formatDateTime")

def hash_file_md5(filename):
    h = md5()
    f = open(filename, "rb")
    while True:
        # Hash 32kB chunks
        data = f.read(32*1024)
        if not data:
            break
        h.update(data)
    f.close()
    return h.hexdigest()
__all__.append("hash_file_md5")



def unicodise(string, encoding = None, errors = "replace"):
    """
    Convert 'string' to Unicode or raise an exception.
    """
    if not encoding:
        encoding = Config.Config().encoding

    if type(string) == unicode:
        return string
    debug("Unicodising %r using %s" % (string, encoding))
    try:
        return string.decode(encoding, errors)
    except UnicodeDecodeError:
        raise UnicodeDecodeError("Conversion to unicode failed: %r" % string)
__all__.append("unicodise")

def deunicodise(string, encoding = None, errors = "replace"):
    """
    Convert unicode 'string' to <type str>, by default replacing
    all invalid characters with '?' or raise an exception.
    """

    if not encoding:
        encoding = Config.Config().encoding

    if type(string) != unicode:
        return str(string)
    debug("DeUnicodising %r using %s" % (string, encoding))
    try:
        return string.encode(encoding, errors)
    except UnicodeEncodeError:
        raise UnicodeEncodeError("Conversion from unicode failed: %r" % string)
__all__.append("deunicodise")

def unicodise_safe(string, encoding = None):
    """
    Convert 'string' to Unicode according to current encoding 
    and replace all invalid characters with '?'
    """

    return unicodise(deunicodise(string, encoding), encoding).replace(u'\ufffd', '?')
__all__.append("unicodise_safe")

def replace_nonprintables(string):
    """
    replace_nonprintables(string)

    Replaces all non-printable characters 'ch' in 'string'
    where ord(ch) <= 26 with ^@, ^A, ... ^Z
    """
    new_string = ""
    modified = 0
    for c in string:
        o = ord(c)
        if (o <= 31):
            new_string += "^" + chr(ord('@') + o)
            modified += 1
        elif (o == 127):
            new_string += "^?"
            modified += 1
        else:
            new_string += c
    if modified and Config.Config().urlencoding_mode != "fixbucket":
        warning("%d non-printable characters replaced in: %s" % (modified, new_string))
    return new_string
__all__.append("replace_nonprintables")

def sign_string(string_to_sign):
    #debug("string_to_sign: %s" % string_to_sign)
    signature = base64.encodestring(hmac.new(Config.Config().secret_access_key, string_to_sign, sha1).digest()).strip()
    #debug("signature: %s" % signature)
    return signature
__all__.append("sign_string")

if __name__ == '__main__':
    pass
