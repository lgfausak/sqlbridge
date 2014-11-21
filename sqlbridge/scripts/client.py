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

import sys, os, argparse, six, json

import twisted
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.wamp import ApplicationRunner
from autobahn.wamp import types

import argparse

from autobahn.twisted.wamp import ApplicationSession,ApplicationRunner

from autobahn.wamp import auth
from autobahn.wamp import types

class Component(ApplicationSession):
    """
    An application component demonstrating client database access
    """

    def __init__(self, *args, **kwargs):
        log.msg("__init__")

        self.db = {}
        self.svar = {}

        log.msg("got args {}, kwargs {}".format(args,kwargs))

        # reap init variables meant only for us
        for i in ( 'topic_base', 'authinfo', 'debug', 'db_call', 'db_query', 'db_args', ):
            if i in kwargs:
                if kwargs[i] is not None:
                    self.svar[i] = kwargs[i]
                del kwargs[i]

        log.msg("sending to super.init args {}, kwargs {}".format(args,kwargs))
        ApplicationSession.__init__(self, *args, **kwargs)

    def onConnect(self):
        log.msg("onConnect")
        auth_type = 'none'
        auth_user = 'anon'
        if 'authinfo' in self.svar:
            auth_type = self.svar['authinfo']['auth_type']
            auth_user = self.svar['authinfo']['auth_user']
        log.msg("onConnect with {} {}".format(auth_type, auth_user))
        self.join(self.config.realm, [six.u(auth_type)], six.u(auth_user))

    def onChallenge(self, challenge):
        log.msg("onChallenge - maynard")
        password = 'unknown'
        if 'authinfo' in self.svar:
            password = self.svar['authinfo']['auth_password']
        log.msg("onChallenge with password {}".format(password))
        if challenge.method == u'wampcra':
            if u'salt' in challenge.extra:
                key = auth.derive_key(password.encode('utf8'),
                    challenge.extra['salt'].encode('utf8'),
                    challenge.extra.get('iterations', None),
                    challenge.extra.get('keylen', None))
            else:
                key = password.encode('utf8')
            signature = auth.compute_wcs(key, challenge.extra['challenge'].encode('utf8'))
            return signature.decode('ascii')
        else:
            raise Exception("don't know how to compute challenge for authmethod {}".format(challenge.method))

    def watch_callback_function(self, details):
        log.msg("watch: {}".format(details))
        print("watch: {}").format(details)

        self.disconnect()

        return

    @inlineCallbacks
    def onJoin(self, details):
        log.msg("db:onJoin session attached {}".format(details))
        dcon = False

        # query, operation or watch
        try:
            log.msg("topic_base: {}".format(self.svar['topic_base']))
            log.msg("db_call: {}".format(self.svar['db_call']))
            log.msg("db_query: {}".format(self.svar['db_query']))
            log.msg("db_args: {}".format(self.svar['db_args']))
            rv = yield self.call(self.svar['topic_base'] + '.' + self.svar['db_call'],
                    self.svar['db_query'], self.svar['db_args'])
        except Exception as err:
            log.msg("db:onJoin error {}".format(err))
            dcon = True
        else:
            if self.svar['db_call'] == 'query':
                log.msg("db:onJoin query(SUCCESS) : {}".format(json.dumps(rv,indent=4)))
                print("{}").format(json.dumps(rv,indent=4))
                dcon = True
            elif self.svar['db_call'] == 'operation':
                log.msg("db:onJoin operation(SUCCESS)")
                dcon = True
            elif self.svar['db_call'] == 'info':
                log.msg("db:onJoin info(SUCCESS)")
                print("{}").format(json.dumps(rv,indent=4))
                dcon = True
            elif self.svar['db_call'] == 'watch':
                log.msg("db:onJoin watch(SUCCESS) : subscribing to: {}".format(rv))
                rv = yield self.subscribe(self.watch_callback_function, rv)
            else:
                log.msg("db:onJoin error, don't know db_call : {}".format(db_call))
                dcon = True

        if dcon:
            log.msg("db:onJoin disconnecting : {}")
            self.disconnect()

    def onLeave(self, details):
        print("onLeave: {}").format(details)

        self.disconnect()

        return

    def onDisconnect(self):
        print("onDisconnect:")
        reactor.stop()

def run():
    prog = os.path.basename(__file__)

    def_wsocket = 'ws://127.0.0.1:8080/ws'
    def_user = 'client'
    def_secret = 'clientsecret'
    def_realm = 'realm1'
    def_topic_base = 'com.db'
    def_db_call = 'query'
    def_db_query = 'select 1'
    def_db_args = '{}'

    p = argparse.ArgumentParser(description="run sqlbridge command")

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
            help='your query will be executed against this topic base, the default: ' + def_topic_base)
    p.add_argument('-c', '--call', action='store', dest='db_call', default=def_db_call,
            help='this is concatenated with topic_base after prepending a dot, default : ' + def_db_call)
    p.add_argument('-q', '--query', action='store', dest='db_query', default=def_db_query,
            help='this is the first argument to db_call, if db_call is operation or query then this is the sql query to run. If the operation is watch then this is the LISTEN to watch : ' + def_db_query)
    p.add_argument('-a', '--args', action='store', dest='db_args', default=def_db_args,
            help='if your query requires arguments they can be specified in json format here, default is a blank dictionary : ' + def_db_args)

    args = p.parse_args()
    if args.verbose:
       log.startLogging(sys.stdout)

    component_config = types.ComponentConfig(realm=args.realm)
    ai = {
            'auth_type':'wampcra',
            'auth_user':args.user,
            'auth_password':args.password
            }
    mdb = Component(config=component_config,
            authinfo=ai,topic_base=args.topic_base,debug=args.verbose,
            db_call=args.db_call,db_query=args.db_query,db_args=json.loads(args.db_args))
    runner = ApplicationRunner(args.wsocket, args.realm)
    runner.run(lambda _: mdb)


if __name__ == '__main__':
   run()
