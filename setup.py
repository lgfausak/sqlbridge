###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import
import os
from glob import glob
from os.path import join

import sys
import platform
from setuptools import setup, find_packages


LONGSDESC = """
sqlbridge|Web Socket sqlbridge for Autobahn

More information:

* `sqlbridge Site <http://github.com/lgfausak/sqlbridge>`__
"""

## get version string from "__init__.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="sqlbridge/__init__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


## Now install sqlbridge ..
##
setup(
   name = 'sqlbridge',
   version = verstr,
   description = 'sql bridge for Autobahn|Python.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'Greg Fausak',
   author_email = 'lgfausak@gmail.com',
   url = 'https://github.com/lgfausak/sqlbridge',
   platforms = 'Any',
   install_requires = ['autobahn==0.9.2', 'twisted>=14.0.2', 'taskforce>=0.1.9'],
   extras_require = {
      ## Twisted/txpostgres needed for PostgreSQL support
      ## mysql needs the python import libraries
      'postgres': ['txpostgres>=1.2.0','psycopg2>=2.5.4'],
      'mysql': ['MySQL-python>=1.2.3'],
   },
   entry_points = {
      'console_scripts': [
         'sqlbridge = sqlbridge.scripts.cli:run',
         'sqlcmd = sqlbridge.scripts.client:run',
         'sqlrouter = sqlbridge.scripts.basicrouter:run',
      ]},
   packages = find_packages(),
   include_package_data = True,
   package_data = {
       ".": [ "LICENSE" ]
   },
   data_files=[('sqlbridge', glob('config/*.conf'))],
   zip_safe = True,
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 4 - Beta",
                  "Environment :: No Input/Output (Daemon)",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Programming Language :: Python :: 2",
                  "Programming Language :: Python :: 2.6",
                  "Programming Language :: Python :: 2.7",
                  "Programming Language :: Python :: Implementation :: CPython",
                  "Programming Language :: Python :: Implementation :: PyPy",
                  "Programming Language :: Python :: Implementation :: Jython",
                  "Topic :: Internet",
                  "Topic :: Internet :: WWW/HTTP",
                  "Topic :: Communications",
                  "Topic :: System :: Distributed Computing",
                  "Topic :: Software Development :: Libraries",
                  "Topic :: Software Development :: Libraries :: Python Modules",
                  "Topic :: Software Development :: Object Brokering"],
   keywords = 'autobahn websocket wamp rpc pubsub twisted database sql postgres mysql sqlite'
)
