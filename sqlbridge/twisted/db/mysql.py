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
## mysql.py - mysql driver
##
## this is driver interface code.  It is used with the DB class.  It shouldn't
## be called or instantiated independent of that class.
###############################################################################

from __future__ import absolute_import
import sys,os
import MySQLdb
from twisted.enterprise import adbapi
from twisted.python import log
from twisted.internet.defer import inlineCallbacks, returnValue

from .dbbase import dbbase

class MYSQL14_14(dbbase):
    """
    basic mysql 14.14 driver
    """

    def __init__(self, topic_base, app_session, debug):
        if debug is not None and debug:
            log.startLogging(sys.stdout)
        log.msg("MYSQL14_14:__init__()")
        self.engine_version = "MYSQL14_14"
        self.engine = "MYSQL"
        self.conn = None
        self.dsn = None
        self.topic_base = topic_base
        self.app_session = app_session
        self.debug = debug
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
    def connect(self,*args,**kwargs):
        log.msg("MYSQL14_14:connect({} {})".format(args, kwargs))
        self.dsn = args[0]
        # there must be an easier way.
        # this converts db=x host=y shatever=z to a dictionary.
        #dd=json.loads('{'+','.join(re.sub(r'([a-z0-9_-]*)=([a-z0-9_-]*)','"\\1":"\\2"',dsn).split())+'}')
        try:
            self.conn = adbapi.ConnectionPool("MySQLdb",**dict(s.split('=') for s in self.dsn.split()))
            log.msg("MYSQL14_14:connect() established")
        except Exception as err:
            log.msg("MYSQL14_14:connect({}),error({})".format(self.dsn,err))
            raise err
        return

    #
    # disconnect
    #   this disconnects from the currently connected database.  if no database
    #   is currently connected then this does nothing.
    def disconnect(self, *args, **kwargs):
        log.msg("MYSQL14_14:disconnect({},{})".format(args,kwargs))
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
    #  method to use, use operation instead
    #

    @inlineCallbacks
    def query(self,*args, **kwargs):
        log.msg("MYSQL14_14:query() ARGS:{} KWARGS:{}".format(args, kwargs))
        s = args[0]
        a = args[1]
        if self.conn:
            try:
                log.msg("MYSQL14_14:query().running({} with args {})".format(s,a))
                rv = yield self.conn.runQuery(s,a)
                log.msg("MYSQL14_14:query().results({})".format(rv))
                returnValue(rv)
            except Exception as err:
                log.msg("MYSQL14_14:query({}),error({})".format(s,err))
                raise err

        # error here, probably should raise exception
        return

    #
    # operation:
    #  identical to query, except, there is no result returned.
    # note:
    #  it is important that your query does NOT return anything!  If it does,
    #  use the query call!
    #
    # see also:
    #  query method has a good description of this and query.
    #

    @inlineCallbacks
    def operation(self,*args, **kwargs):
        log.msg("MYSQL14_14:operation() ARGS:{} KWARGS:{}".format(args, kwargs))
        s = args[0]
        a = args[1]
        if self.conn:
            try:
                log.msg("MYSQL14_14:query().running({} with args {})".format(s,a))
                rv = yield self.conn.runOperation(s,a)
                log.msg("MYSQL14_14:query().results({})".format(rv))
                returnValue(rv)
            except Exception as err:
                log.msg("MYSQL14_14:query({}),error({})".format(s,err))
                raise err

        # error here, probably should raise exception
        return

    #
    # watch:
    #  this is specific to postgres NOTIFY/LISTEN. other drivers will need to stub this out
    #

    def watch(self,*args,**kwargs):
        raise Exception("mysql is trying to add watch, can only do this in postgres ")
        return

    #
    # info:
    #  return information about this connection
    #

    @inlineCallbacks
    def info(self,*args,**kwargs):
        log.msg("MYSQL14_14:info({},{})".format(args,kwargs))
        rv = yield [{
            "engine":self.engine,
            "engine_version":self.engine_version,
            "dsn":self.dsn,
            "topic_base":self.topic_base,
            "debug":self.debug
        }]
        returnValue(rv)
        return
