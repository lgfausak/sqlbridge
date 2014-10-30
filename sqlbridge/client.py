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
from autobahn.twisted.wamp import ApplicationRunner, ApplicationSession

from autobahn import util

class Component(ApplicationSession):
   """
   This component just runs an sql command, displays results, exits.
   You need to 
   """

   def onJoin(self, details):
      print("session attached")

      def got(res, started, msg):
         duration = 1000. * (time.clock() - started)
         print("{}: {} in {}".format(msg, res, duration))

      t1 = time.clock()
      d1 = self.call('com.math.slowsquare', 3)
      d1.addCallback(got, t1, "Slow Square")

      t2 = time.clock()
      d2 = self.call('com.math.square', 3)
      d2.addCallback(got, t2, "Quick Square")

      def done(_):
         print("All finished.")
         self.leave()

      DeferredList ([d1, d2]).addBoth(done)


   def onDisconnect(self):
      print("disconnected")
      reactor.stop()


def run():
    prog = os.path.basename(__file__)

    def_wsocket = 'ws://127.0.0.1:8080/ws'
    def_user = 'db'
    def_secret = 'dbsecret'
    def_realm = 'realm1'
    def_topic_base = 'com.db'
    def_query = 'select * from login'

    p = argparse.ArgumentParser(description="db admin manager for autobahn")

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
    p.add_argument('-t', '--topic', action='store', dest='topic_base', default=def_topic_base,
                        help='if you specify --dsn then you will need a topic to root it on, the default ' + def_topic_base + ' is fine.')
    p.add_argument('-q', '--query', action='store', dest='query', default=def_query,
                        help='specify a query to run, the default ' + def_query + ' is an example.')

    args = p.parse_args()
    if args.verbose:
       log.startLogging(sys.stdout)

    runner = ApplicationRunner(args.wsocket, args.realm)
    runner.run(Component)


if __name__ == '__main__':
   run()
