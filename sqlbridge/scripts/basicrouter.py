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

import sys, argparse, os

from twisted.python import log
from twisted.internet.endpoints import serverFromString
from autobahn.twisted.choosereactor import install_reactor
from autobahn.twisted.wamp import RouterFactory
from autobahn.twisted.wamp import RouterSessionFactory
from autobahn.twisted.websocket import WampWebSocketServerFactory

from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.resource import Resource

class DemoJavascriptPage(Resource):
    isLeaf = True
    def __init__(self, args):
        self.args = args

    def render_GET(self, request):
        return '''
<html>
<head>
<title>Simple Autobahn SQLBridge</title>
<script src="https://autobahn.s3.amazonaws.com/autobahnjs/latest/autobahn.min.jgz">
</script>
<script language="Javascript">
var my_session;
var connection = new autobahn.Connection({
         url: '%s',
         realm: '%s'
      });

connection.onopen = function (session) {
   my_session = session;
};

connection.open();

function doit() {
   query = document.getElementById('query').value;
   try {
      args = JSON.parse(document.getElementById('args').value);
   } catch(err) {
      args = {};
   }

   console.log("run query ", query);

   abcall = '%s.' + document.getElementById("abcall").value;

   my_session.call(abcall, [ query, args ] ).then(
      function (res) {
         console.log("Result:", res);
         if(res) {
            tbtext = "<table>";
            tbtext += "<theader>";
            ri = res[0]
            for(j in ri) {
               if(!ri.hasOwnProperty(j)) {
                  continue;
               }
               tbtext += "<th>";
               tbtext += j;
               tbtext += "</th>";
            }
            tbtext += "</theader>";
            tbtext += "<tbody>";
            for(i = 0; i < res.length; i++) {
              ri = res[i];
              tbtext += "<tr>";
              for(j in ri) {
                 if(!ri.hasOwnProperty(j)) {
                    continue;
                 }
                 tbtext += "<td>";
                 tbtext += ri[j];
                 tbtext += "</td>";
              }
              tbtext += "</tr>";
            }
            tbtext += "</tbody>";
            tbtext += "</table>";
            document.getElementById("result").innerHTML = tbtext;
         }
         tbtext = "<p>Autobahn call: " + abcall + "</p>";
         tbtext += "<p>Query: " + query + "</p>";
         tbtext += "<p>Args: " + JSON.stringify(args) + "</p>";
         document.getElementById("rpc").innerHTML = tbtext;
      },
      function(error) {
         console.log(JSON.stringify(error));
         document.getElementById("rpc").innerHTML = "Error : " + JSON.stringify(error);
      }
   )
}

</script>
</head>
<body>
<form name="f1">
  <p>type:
  <select id="abcall">
    <option value="query">query (results are expected, like select)</option>>
    <option value="operation">operation (no results expected, like delete from)</option>>
    <option value="watch">watch (only valid for postgres databases)</option>>
  </select></p>
  <p>query: <textarea rows="6" cols="60" id="query" name="query"></textarea></p>
  <p>args (json format): <input size="60" id="args" name="args" type="text"/>  </p>
  <p><input value="Go" type="button" onclick='JavaScript:doit()'/></p>
  <hr/>
  <div id="rpc"></div>
  <hr/>
  <div id="result"></div>
  <hr/>
</form>
</body>
</html>
        ''' % ( self.args.wsocket, self.args.realm, self.args.topic_base, )

def run():
    prog = os.path.basename(__file__)

    def_endpoint = 'tcp:8080'
    def_wsocket = 'ws://127.0.0.1:8080/ws'
    def_webserviceport = '8000'
    def_user = 'db'
    def_secret = 'dbsecret'
    def_realm = 'realm1'
    def_topic_base = 'com.db'

    # http://stackoverflow.com/questions/3853722/python-argparse-how-to-insert-newline-the-help-text
    p = argparse.ArgumentParser(description="db admin manager for autobahn")

    p.add_argument("-e", "--endpoint", action='store', type = str, dest='endpoint', default = def_endpoint,
            help = 'Twisted server endpoint descriptor, e.g. "tcp:8080" or "unix:/tmp/mywebsocket", default is: ' + def_endpoint)
    p.add_argument("-p", "--port", action='store', type = int, dest='port', default = def_webserviceport,
            help = 'Web service serving demojavapage listens on port, default: ' + def_webserviceport)
    p.add_argument('-w', '--websocket', action='store', dest='wsocket', default=def_wsocket,
                        help='web socket definition (what the demo javascript page connects to), default is: '+def_wsocket)
    p.add_argument('-r', '--realm', action='store', dest='realm', default=def_realm,
                        help='connect to websocket using realm, default is: '+def_realm)
    p.add_argument('-v', '--verbose', action='store_true', dest='verbose',
            default=False, help='Verbose logging for debugging')
    p.add_argument('-t', '--topic', action='store', dest='topic_base', default=def_topic_base,
                        help='if you specify --dsn then you will need a topic to root it on, the default ' + def_topic_base + ' is fine.')

    args = p.parse_args()
    if args.verbose:
       log.startLogging(sys.stdout)

    ## we use an Autobahn utility to install the "best" available Twisted reactor
    ##
    reactor = install_reactor()
    print("Running on reactor {}".format(reactor))

    router_factory = RouterFactory()
    session_factory = RouterSessionFactory(router_factory)
    transport_factory = WampWebSocketServerFactory(session_factory, debug = args.verbose)
    transport_factory.setProtocolOptions(failByDrop = False)
    server = serverFromString(reactor, args.endpoint)
    server.listen(transport_factory)

    resource = DemoJavascriptPage(args)
    factory = Site(resource)
    reactor.listenTCP(args.port, factory)

    reactor.run()

if __name__ == '__main__':
    run()
