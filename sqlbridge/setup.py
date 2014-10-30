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

import sys
import platform
from setuptools import setup, find_packages


LONGSDESC = """
sqlbridge|Python sqlbridge for Autobahn

More information:

* `Autobahn Site <http://autobahn.ws/python>`__
* `sqlbridge Site <http://autobahn.ws/python>`__
* `Source Code <https://github.com/tavendo/AutobahnPython>`__
"""

## get version string from "autobahn/__init__.py"
## See: http://stackoverflow.com/a/7071358/884770
##
import re
VERSIONFILE="autobahnaddons/__init__.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


## Now install Autobahn ..
##
setup(
   name = 'autobahnaddons',
   version = verstr,
   description = 'Autobahn|Python add-ons.',
   long_description = LONGSDESC,
   license = 'Apache License 2.0',
   author = 'AutobahnPython Contributors',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://autobahn.ws/python',
   platforms = 'Any',
   install_requires = ['autobahn>=0.9.2'],
   extras_require = {
      ## Twisted/txpostgres needed for PostgreSQL support
      'postgres': ['twisted>=14.0.2', 'txpostgres>=1.2.0'],
   },
   entry_points = {
      'console_scripts': [
         'sqlbridge = autobahnaddons.sqlbridge.cli:run',
         'sqlcmd = autobahnaddons.sqlbridge.client:run',
      ]},
   packages = find_packages(),
   include_package_data = True,
   data_files = [('.', ['LICENSE'])],
   zip_safe = True,
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: Apache Software License",
                  "Development Status :: 5 - Production/Stable",
                  "Environment :: No Input/Output (Daemon)",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Programming Language :: Python :: 2",
                  "Programming Language :: Python :: 2.6",
                  "Programming Language :: Python :: 2.7",
                  "Programming Language :: Python :: 3",
                  "Programming Language :: Python :: 3.3",
                  "Programming Language :: Python :: 3.4",
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
   keywords = 'autobahn autobahn.ws websocket realtime rfc6455 wamp rpc pubsub twisted asyncio'
)
