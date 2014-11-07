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


import sys, argparse

from twisted.python import log
from twisted.internet.endpoints import serverFromString
from autobahn.twisted.choosereactor import install_reactor
from autobahn.twisted.wamp import RouterFactory
from autobahn.twisted.wamp import RouterSessionFactory
from autobahn.twisted.websocket import WampWebSocketServerFactory

def run():
   ## parse command line arguments
   ##
   parser = argparse.ArgumentParser()

   parser.add_argument("-d", "--debug", action = "store_true",
                       help = "Enable debug output.")

   parser.add_argument("--endpoint", type = str, default = "tcp:8080",
                       help = 'Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket".')

   args = parser.parse_args()
   log.startLogging(sys.stdout)

   ## we use an Autobahn utility to install the "best" available Twisted reactor
   ##
   reactor = install_reactor()
   print("Running on reactor {}".format(reactor))

   router_factory = RouterFactory()
   session_factory = RouterSessionFactory(router_factory)
   transport_factory = WampWebSocketServerFactory(session_factory, debug = args.debug)
   transport_factory.setProtocolOptions(failByDrop = False)
   server = serverFromString(reactor, args.endpoint)
   server.listen(transport_factory)

   reactor.run()

if __name__ == '__main__':
    run()
