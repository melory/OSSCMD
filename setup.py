#!/usr/bin/env python
# -*- coding: utf-8 -*-
## ossbrowser
## Author: melory
## Email:imsrch@melory.me
## License: GPL Version 2

from distutils.core import setup
import sys
import os

import osscmdlib.pkginfo as pkginfo

if float("%d.%d" % sys.version_info[:2]) < 2.4:
	sys.stderr.write("Your Python version %d.%d.%d is not supported.\n" % sys.version_info[:3])
	sys.stderr.write("osscmd requires Python 2.4 or newer.\n")
	sys.exit(1)

man_path = "share/man"
doc_path = "share/doc/packages"
data_files = [	
	(doc_path+"/osscmd", [ "README", "INSTALL" ]),
]

## Main distutils info
setup(
	## Content description
	name = pkginfo.package,
	version = pkginfo.version,
	packages = ['oss', 'osscmdlib'],
	scripts = ['osscmd'],
	data_files = data_files,

	## Packaging details
	author = "linjiudui",
	author_email = "linjd828917@gmail.com",
	license = pkginfo.license,
	description = pkginfo.short_description,
	long_description = pkginfo.long_description
)
