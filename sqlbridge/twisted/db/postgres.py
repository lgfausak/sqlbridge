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

###############################################################################
## postgres.py - postgres driver
##
## this is driver interface code.  It is used with the DB class.  It shouldn't
## be called or instantiated independent of that class.
###############################################################################

from __future__ import absolute_import
import sys,os,string,random,types
import six
import psycopg2
import psycopg2.extras
from psycopg2.extensions import SQL_IN, register_adapter
from txpostgres import txpostgres

from twisted.python import log
from twisted.internet.defer import inlineCallbacks, returnValue

from .dbbase import dbbase

def rdc(*args, **kwargs):
    kwargs['connection_factory'] = psycopg2.extras.RealDictConnection
    # this is to let everything pass through as strings
    psycopg2.extensions.string_types.clear()
    register_adapter(list, SQL_IN)
    return psycopg2.connect(*args, **kwargs)

#
# this class is set up to use the RealDictConnection instead of the default
# one.  This means that we can use a dictionary to contain arguments
# passed to queries.  This is pretty handy.
#
# also slipped in here is the extensions.string_types.clear().
# i like this a lot, but, others may not.  when you run a query, the
# results are returned in types that make sense for the column queried.  like,
# a timestamp is returned in a python date object.  A decimal is returned in
# a number object, etc.. I simply want a behavior where the column
# is always returned in text. It makes things like serializing a
# query result.  Otherwise, all types would have to be converted to text
# before the return value could be serialized (and pushed over the autobahn wire).
#
class RDC(txpostgres.Connection):
        connectionFactory = staticmethod(rdc)

class PG9_4(dbbase):
    """
    basic postgres 9.4 driver
    """

    def __init__(self, topic_base, app_session, debug):
        if debug is not None and debug:
            log.startLogging(sys.stdout)

        log.msg("PG9_4:__init__()")
        self.engine_version = "PG9_4"
        self.engine = "PG"
        self.conn = None
        self.dsn = None
        self.d = None
        self.topic_base = topic_base
        self.app_session = app_session
        self.wlist = {}
        self.debug = debug
        if debug:
            log.startLogging(sys.stdout)

        return
 
    #
    # connect
    #  simply connect to a database
    #  dsn is the only argument, it is a string, in psycopg2 connect
    #  format.  basically it looks like
    #  dbname=DBNAME host=MACHINE user=DBUSER
    #  DBNAME is the database name
    #  MACHINE is the ip address or dns name of the machine
    #  DBUSER is the user to connect as
    #
    @inlineCallbacks
    def connect(self,*args,**kwargs):
        log.msg("PG9_4:connect({},{})".format(args,kwargs))
        self.dsn = args[0]
        self.conn = RDC()
        try:
            rv = yield self.conn.connect(self.dsn)
            log.msg("PG9_4:connect() established")
        except Exception as err:
            log.msg("PG9_4:connect({}),error({})".format(dsn,err))
            raise err
        return

    #
    # disconnect
    #   this disconnects from the currently connected database.  if no database
    #   is currently connected then this does nothing.
    def disconnect(self,*args,**kwargs):
        log.msg("PG9_4:disconnect({},{})".format(args,kwargs))
        if self.conn:
            c = self.conn
            self.conn = None
            c.close()

        return

    #
    # query:
    #  s - query to run (with dictionary substitution embedded, like %(key)s
    #  a - dictionary pointing to arguments.
    # example:
    #  s = 'select * from login where id = %(id)s'
    #  a = { 'id': 100 }
    # returns:
    #  dictionary result of query
    # note:
    #  there MUST be a result, otherwise use the operation call!
    #  well, the query can return 0 rows, that is ok.  but, if the query
    #  by its nature doesn't return any rows then don't use this call!
    #  for example, a query that says 'insert into table x (c) values(r)'
    #  by its nature it doesn't return a row, so, this isn't the right
    #  method to use, use operation instead.
    # note:
    #  s and a can be arrays instead of single, in that case the entire
    #  array is run as a single atomic transaction, they all work, or all fail.
    #  further, a can be an array of length 1, in which case the same arguments
    #  are used for all of the queries in s, otherwise, a must be an array of the
    #  same length as s, which would indicate a separate set of arguments for
    #  each of the queries in array s.
    #

    @inlineCallbacks
    def query(self,*args, **kwargs):
        log.msg("PG9_4:query() ARGS:{} KWARGS:{}".format(args, kwargs))
        if len(args) < 1:
            log.msg("PG9_4:query(), required to have at least one argument")
            raise Exception("PG9_4:query(), required to have at least one argument")
        qsa = args[0]
        if isinstance(qsa, types.StringTypes):
            qsa = [ args[0] ]
        elif not isinstance(qsa,types.ListType):
            log.msg("PG9_4:query(), first argument must be string or array of strings:{}".format(args[0]))
            raise Exception("PG9_4:query(), first argument must be string or array of strings:{}".format(args[0]))
        asa = []
        if len(args) > 1:
            asa = args[1]
            if isinstance(asa, types.DictType):
                asa = [ args[1] for i in range(len(qsa)) ]
            elif not isinstance(asa,types.ListType):
                log.msg("PG9_4:query(), second argument must be dict or array of dicts:{}".format(args[1]))
                raise Exception("PG9_4:query(), second argument must be dict or array of dicts:{}".format(args[1]))
        else:
            asa = [ {} for i in range(len(qsa)) ]

        # qsa contains an array of queries to run
        # asa contains an array of dicts as arguments for those queries
        if self.conn:
            try:
                log.msg("PG9_4:query().details.caller {}".format(kwargs['details'].caller))
                log.msg("PG9_4:query().details.authid {}".format(kwargs['details'].authid))
                log.msg("PG9_4:query().details.authrole {}".format(kwargs['details'].authrole))
                log.msg("PG9_4:query().details.authmethod {}".format(kwargs['details'].authmethod))
                log.msg("PG9_4:query().details.caller_transport {}".format(kwargs['details'].caller_transport))
                # we run an interaction to keep together the
                # set_session_variable() with the 
                # query.  so, if stuff is deleted/updated/inserted
                # the auditing mechanisms have the authid
                # set to create an audit trail
                @inlineCallbacks
                def interaction(cur):
                    if 'details' in kwargs and kwargs['details'].caller is not None:
                        details = kwargs['details']
                        iv = yield cur.execute("select * from private.set_session(%(session_id)s)",
                            {'session_id':int(details.caller)})
                        ivf = iv.fetchall()
                        log.msg("PG9_4:iv {}".format(ivf))
                    rsa = []
                    for qi in range(len(qsa)):
                        log.msg("PG9_4:query index {}:{}:{}".format(qi,qsa[qi],asa[qi]))
                        rv = yield cur.execute(qsa[qi], asa[qi])
                        rvf = rv.fetchall()
                        log.msg("PG9_4:rv {}".format(rvf))
                        rsa.append(rvf)
                    returnValue(rsa)
                    return

                rv = yield self.conn.runInteraction(interaction)
                # here is a convenience, if a single query is run (only one
                # query in args[0]) then a single result is returned eliminating
                # the need for an array of results.
                if len(rv) == 1:
                    returnValue(rv[0])
                else:
                    returnValue(rv)
            except Exception as err:
                log.msg("PG9_4:query({}),error({})".format(qsa,err))
                raise err

        # error here, probably should raise exception
        log.msg("PG9_4:query() attempt, but there is no connection")
        return

    #
    # operation:
    #  identical to query, except, there is no result returned.
    # note:
    #  it is important that your query does NOT return anything!  If it does,
    #  use the query call!
    #

    @inlineCallbacks
    def operation(self,*args, **kwargs):
        log.msg("PG9_4:operation() ARGS:{} KWARGS:{}".format(args, kwargs))
        s = args[0]
        a = args[1]
        if self.conn:
            try:
                log.msg("PG9_4:operation().running({} with args {})".format(s,a))
                if 'details' in kwargs and kwargs['details'].authid is not None:
                    details = kwargs['details']
                    log.msg("details.authid {}".format(details.authid))

                    # we run an interaction to keep together the
                    # set_session_variable() with the 
                    # operation.  so, if stuff is deleted/updated/inserted
                    # the auditing mechanisms have the authid
                    # set to create an audit trail
                    @inlineCallbacks
                    def interaction(cur):
                        yield cur.execute("select * from private.set_session_variable('audit_user',%(user_id)s)",
                            {'user_id':str(details.authid)})
                        rv = yield cur.execute(s, a)
                        returnValue(True)
                        return
                    rv = yield self.conn.runInteraction(interaction)
                    returnValue(rv)
                else:
                    rv = yield self.conn.runOperation(s,a)
                    returnValue(rv)
                log.msg("PG9_4:operation().results({})".format(rv))
            except Exception as err:
                log.msg("PG9_4:operation({}),error({})".format(s,err))
                raise err

        # error here, probably should raise exception
        return

    #
    # watch:
    #  for LISTEN side of NOTIFY.
    # note:
    #  handy function that lets us register a function to call
    #  when a LISTEN is triggered.  This is async database notification.
    #
    # see also:
    #  http://txpostgres.readthedocs.org/en/latest/usage.html#listening-for-database-notifications
    #

    @inlineCallbacks
    def watch_func(self, notify):
        log.msg("PG9_4:watch_func: notify {}".format(notify))

        if notify.channel in self.wlist:
            log.msg("PG9_4:watch_func: word in list, publish to {}".format(self.wlist[notify.channel]['topic']))
            yield self.app_session.publish(six.u(self.wlist[notify.channel]['topic']), notify.payload)

    @inlineCallbacks
    def watch(self,*args,**kwargs):
        log.msg("PG9_4:watch() ARGS:{} KWARGS:{}".format(args, kwargs))
        word = args[0].lower()
        if self.conn is None:
            raise Exception("cannot add watch because there is no connection {}".format(word))

        # if there is nothing in the watch list, then this is the first watch
        # call.  that being the case we need to set a method to receive the
        # listen event.

        if len(self.wlist) == 0:
            self.conn.addNotifyObserver(self.watch_func)

        if word not in self.wlist:
            s = 'listen' + word
            rv = yield self.conn.runOperation('listen ' + word)
            self.wlist[word] = { 'topic':self.topic_base + '.watch.' +
                    ''.join(random.choice(string.ascii_lowercase) for _ in range(8)) }

        returnValue(self.wlist[word]['topic'])

        return

    #
    # info:
    #  return information about this connection
    #

    @inlineCallbacks
    def info(self,*args,**kwargs):
        log.msg("PG9_4:info({},{})".format(args,kwargs))
        rv = yield [{
            "engine":self.engine,
            "engine_version":self.engine_version,
            "dsn":self.dsn,
            "topic_base":self.topic_base,
            "debug":self.debug
        }]

        returnValue(rv)

        return
