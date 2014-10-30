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
## dbbase.py - base database driver
##
## this is driver interface code.  It is used with the DB class.  It shouldn't
## be called or instantiated independent of that class.  Currently there are two
## drivers that use this code, postgres and mysql.  To add another database
## you can do so by subclassing this abstract class, overriding the methods,
## and adding the new class to db.py
###############################################################################

from abc import ABCMeta, abstractmethod

class dbbase(object):
    __metaclass__ = ABCMeta
    """
    base database driver
    """

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
    @abstractmethod
    def connect(self,dsn):
        pass

    #
    # disconnect
    #   this disconnects from the currently connected database.  if no database
    #   is currently connected then this does nothing.
    @abstractmethod
    def disconnect(self):
        pass

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

    @abstractmethod
    def query(self,s,a):
        pass

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

    @abstractmethod
    def operation(self,s,a):
        pass

    #
    # watch:
    #  this is specific to postgres NOTIFY/LISTEN. other drivers will need to stub this out
    #

    @abstractmethod
    def watch(self,s,a):
        pass

