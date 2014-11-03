#!/usr/bin/env python
###############################################################################
##
##  Copyright (C) 2014 Greg Fausak
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##        http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

from __future__ import absolute_import

import sys, os, argparse, six

import twisted
from twisted.python import log

from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp import types

from autobahn import util

from sqlbridge.twisted.dbengine import DB

import argparse

# http://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-the-help-text
class SmartFormatter(argparse.HelpFormatter):

    def _split_lines(self, text, width):
        # this is the RawTextHelpFormatter._split_lines
        if text.startswith('R|'):
            return text[2:].splitlines()  
        return argparse.HelpFormatter._split_lines(self, text, width)

def run():
    prog = os.path.basename(__file__)

    def_wsocket = 'ws://127.0.0.1:8080/ws'
    def_user = 'db'
    def_secret = 'dbsecret'
    def_realm = 'realm1'
    def_topic_base = 'com.db'

    # http://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-the-help-text
    p = argparse.ArgumentParser(description="db admin manager for autobahn", formatter_class=SmartFormatter)

    p.add_argument('-w', '--websocket', action='store', dest='wsocket', default=def_wsocket,
                        help='web socket definition, default is: '+def_wsocket)
    p.add_argument('-r', '--realm', action='store', dest='realm', default=def_realm,
                        help='connect to websocket using realm, default is: '+def_realm)
    p.add_argument('-v', '--verbose', action='store_true', dest='verbose',
            default=False, help='Verbose logging for debugging')
    p.add_argument('-u', '--user', action='store', dest='user', default=def_user,
                        help='connect to websocket as user, default is: '+def_user)
    p.add_argument('-s', '--secret', action='store', dest='password', default=def_secret,
                        help='users "secret" password')
    p.add_argument('-e', '--engine', action='store', dest='engine', default=None,
                        help='if specified, a database engine will be attached.' +
                             ' Note engine is rooted on --topic.' +
                             ' Valid engine options are PG, MYSQL or SQLITE')
    p.add_argument('-d', '--dsn', action='store', dest='dsn', default=None,
                        help='R|if specified the database in dsn will be connected and ready.\n' +
                             'dsns are unique to the engine being used.  Valid examples:' +
                             '\n-----------' +
                             '\nPG: dbname=autobahn host=192.168.200.230 user=autouser password=testpass' +
                             '\nMYSQL: database=autobahn user=autouser password=passtest' +
                             '\nSQLITE: Z')
    p.add_argument('-t', '--topic', action='store', dest='topic_base', default=def_topic_base,
                        help='if you specify --dsn then you will need a topic to root it on, the default ' + def_topic_base + ' is fine.')

    args = p.parse_args()
    if args.verbose:
       log.startLogging(sys.stdout)

    component_config = types.ComponentConfig(realm=args.realm)
    ai = {
            'auth_type':'wampcra',
            'auth_user':args.user,
            'auth_password':args.password
            }
    mdb = DB(config=component_config,
            authinfo=ai,engine=args.engine,topic_base=args.topic_base,dsn=args.dsn, debug=args.verbose)

    runner = ApplicationRunner(args.wsocket, args.realm)
    runner.run(lambda _: mdb)


if __name__ == '__main__':
   run()
