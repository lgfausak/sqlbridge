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

import sys,os,argparse,six

from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks
from twisted.internet.endpoints import clientFromString

#from myapprunner import MyApplicationRunner
from autobahn.twisted.wamp import ApplicationSession,ApplicationRunner

from autobahn import util
from autobahn.wamp import auth
from autobahn.wamp import types
from autobahn.wamp.exception import ApplicationError
from autobahn.twisted import wamp, websocket
from autobahn.twisted.wamp import ApplicationSession

class DB(ApplicationSession):
    """
    An application component providing db access
    """

    def __init__(self, *args, **kwargs):
        log.msg("__init__")

        self.db = {}
        self.svar = {}

        log.msg("got args {}, kwargs {}".format(args,kwargs))

        # reap init variables meant only for us
        for i in ( 'engine', 'topic_base', 'dsn', 'authinfo', 'debug', ):
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

    @inlineCallbacks
    def onJoin(self, details):
        log.msg("db:onJoin session attached {}".format(details))

        if 'engine' in self.svar and 'topic_base' in self.svar:
            if self.svar['engine'] == 'PG9_4' or self.svar['engine'] == 'PG':
                from .db import postgres
                dbo = postgres.PG9_4(topic_base = self.svar['topic_base'], app_session = self, debug = self.svar['debug'])
            elif self.svar['engine'] == 'MYSQL14_14' or self.svar['engine'] == 'MYSQL':
                from .db import mysql
                dbo = mysql.MYSQL14_14(topic_base = self.svar['topic_base'], app_session = self, debug = self.svar['debug'])
            elif self.svar['engine'] == 'SQLITE3_3_8_2' or self.svar['engine'] == 'SQLITE3' or self.svar['engine'] == 'SQLITE':
                from .db import ausqlite3
                dbo = ausqlite3.SQLITE3_3_8_2(topic_base = self.svar['topic_base'], app_session = self, debug = self.svar['debug'])
            else:
                raise Exception("Unsupported dbtype {} ".format(self.svar['engine']))
        else:
            raise Exception("when instantiating this class DB you must provide engine=X and topic_base=Y")

        self.db = { 'instance': dbo }
        self.db['registration'] = {}

        r = types.RegisterOptions(details_arg = 'details')
        self.db['registration']['connect'] = yield self.register(dbo.connect, self.svar['topic_base']+'.connect', options = r)
        self.db['registration']['disconnect'] = yield self.register(dbo.disconnect, self.svar['topic_base']+'.disconnect', options = r)
        self.db['registration']['query'] = yield self.register(dbo.query, self.svar['topic_base']+'.query', options = r)
        self.db['registration']['operation'] = yield self.register(dbo.operation, self.svar['topic_base']+'.operation', options = r)
        self.db['registration']['watch'] = yield self.register(dbo.watch, self.svar['topic_base']+'.watch', options = r)
        self.db['registration']['info'] = yield self.register(dbo.info, self.svar['topic_base']+'.info', options = r)

        if 'dsn' in self.svar:
            log.msg("db:onJoin connecting... {}".format(self.svar['dsn']))
            yield self.call(self.svar['topic_base'] + '.connect', self.svar['dsn'])
            log.msg("db:onJoin connecting established")

        log.msg("db bootstrap procedures registered")

    def onLeave(self, details):
        print("onLeave: {}").format(details)

        yield self.db['registration']['connect'].unregister()
        yield self.db['registration']['disconnect'].unregister()
        yield self.db['registration']['query'].unregister()
        yield self.db['registration']['operation'].unregister()
        yield self.db['registration']['watch'].unregister()
        yield self.db['registration']['info'].unregister()

        del self.db

        self.disconnect()

        return

    def onDisconnect(self):
        print("onDisconnect:")
        reactor.stop()
