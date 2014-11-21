# sqlbridge - Autobahn Database Service
[![Version](https://pypip.in/version/sqlbridge/badge.svg)![Status](https://pypip.in/status/sqlbridge/badge.svg)![Downloads](https://pypip.in/download/sqlbridge/badge.svg)](https://pypi.python.org/pypi/sqlbridge/)[![Build Status](https://travis-ci.org/lgfausak/sqlbridge.svg?branch=master)](https://travis-ci.org/lgfausak/sqlbridge)


SQL Bridge for Autobahn

## Summary

A simple database access component for Autobahn. This component builds bridges to database backends making
them accessible to Autobahn via topics.  The component can be used in its raw form to build custom
Autobahn deployments, or, the convenience scripts that haver been included can be used to
connect an sqlbridge to an already operating Autobahn router.  There are three test scripts included in
this distribution, sqlrouter, sqlbridge and sqlcmd. Brief documentation for each follows. The service
concept here is (in beautiful ascii art):

```
+--------+      +----------+      +-----------+      +---------+
| sqlcmd |<---->| sqlrouter|<---->| sqlbridge |<---->| your db |
| client |      | router   |      |  client   |      | server  |
+--------+      +----------+      +-----------+      +---------+
```

Before sqlcmd (or any client wanting to access the database) can run, first you need:
* A database (postgres, mysql, sqlite).  Installation and feeding beyond the scope
of this documentation.  One thing to note, the database need not be installed
on the sqlbridge client, as long as the sqlbridge client can reach it
via whatever connection mechanism the db server supports. For demonstration purposes you
can just use the sqlite driver, which will create a database on the fly.
* An Autobahn router to connect to.  This can be any router that allows either unchallenged
connectivity, or, wampcra connectivity. For demonstration purposes there is an included
sqlrouter script.
* Once the above two are satisfied, then sqlbridge can be fired up, connecting the Autobahn
router to the db server.
* Finally, once the above three are done, then sqlcmd (or any client) can query
the db server via the sqlbridge.
So without further ado...

## Quick Install
You can just try this:
```
sudo pip install sqlbridge
WANIP=W.X.Y.Z taskforce -r /var/local/sqlbridge/roles.conf -f /var/local/sqlbridge/sqlbridge.conf
```

The WANIP is only important for demo mode.  It sets up a web page which can be accessed from your broswer like:

```
http://W.X.Y.Z:8000/index.html
```

This is a very simple web page which sends queries and displays results.  Note, the same IP address you would use in your browser would
also be used for the WANIP declaration.

The demo mode creates a blank sqlite3 database in the /tmp directory.  The web page gives you access to the database. For
example, you could run these commands:

```
type: operation
query: create table mytable ( name varchar(255) )
```

```
type: operation
query: insert into mytable (name) values ('Mary')
```

```
type: operation
query: insert into mytable (name) values ('Greg')
```

```
type: query
query: select * from mytable
```

The last query will return the two tuples you just inserted into mytable.  The demonstration supports mysql and postgres, however,
installing these and configuring them is going to be up to you.  Once installed and configured, there are two things needed to access
them.  First, you will need to change the roles.conf file.  If you look in there a single line says 'sqlite'.  Simply change that to
'postgres' or 'mysql'.  Second, the sqlbridge.conf file has the dsn necessary to access the postgres or mysql database.  The relevant
section looks like this:

```
        "sqlbridge": {
            "role_defines": {
                "sqlite": {
                    "engine": "SQLITE",
                    "dsn": "database=/tmp/autobahn.sq"
                },
                "postgres": {
                    "engine": "PG",
                    "dsn": "dbname=autobahn host={LANIP} user=autouser"
                },
                "mysql": {
                    "engine": "MYSQL",
                    "dsn": "db=test user=mysql"
                }
            }
        }
```

In this example, if the postgres role was specified, and there was a postgres installation on the same machine with a database called
autobahn, and a user called autouser, the sqlbridge would connect.  Similar comments for mysql. Also, where sqlite3 only supports
'query' operations, mysql and postgres support the idea of 'query' (a command that returns data) and 'operation' (a command
like create table that doesn't return data).  It is important to call the correct one.  If your query returns data, the type is 'query',
otherwise the type is 'operation'.

One further note, postgres supports 'watch'.  My simple javascript page doesn't at this time (although my sqlcmd script does).

## sqlrouter

This is basically copied from the Autobahn examples wamp directory. It is a very basicrouter.
Its only purpose is to help with the demonstration of sqlbridge.

```
usage: sqlrouter [-h] [-d] [--endpoint ENDPOINT]

optional arguments:
  -h, --help           show this help message and exit
  -d, --debug          Enable debug output.
  --endpoint ENDPOINT  Twisted server endpoint descriptor, e.g. "tcp:8080" or
                       "unix:/tmp/mywebsocket".
```

Demonstration mode:
```sh
sqlrouter --endpoint tcp:8080 &
```

## sqlbridge

Command to start database bridge:

```
usage: sqlbridge [-h] [-w WSOCKET] [-r REALM] [-v] [-u USER] [-s PASSWORD]
                 [-e ENGINE] [-d DSN] [-t TOPIC_BASE]

sql bridge for autobahn

optional arguments:
  -h, --help            show this help message and exit
  -w WSOCKET, --websocket WSOCKET
                        web socket definition, default is:
                        ws://127.0.0.1:8080/ws
  -r REALM, --realm REALM
                        connect to websocket using realm, default is: realm1
  -v, --verbose         Verbose logging for debugging
  -u USER, --user USER  connect to websocket as user, default is: db
  -s PASSWORD, --secret PASSWORD
                        users "secret" password
  -e ENGINE, --engine ENGINE
                        if specified, a database engine will be attached. Note
                        engine is rooted on --topic. Valid engine options are
                        PG, MYSQL or SQLITE
  -d DSN, --dsn DSN     if specified the database in dsn will be connected and ready.
                        dsns are unique to the engine being used.  Valid examples:
                        -----------
                        PG: dbname=autobahn host=192.168.200.230 user=autouser password=testpass
                        MYSQL: database=autobahn user=autouser password=passtest
                        SQLITE: Z
  -t TOPIC_BASE, --topic TOPIC_BASE
                        if you specify --dsn then you will need a topic to
                        root it on, the default com.db is fine.
```

valid DRIVERs are:
* PG9\_4	Postgres version v9.4b3 (PG)
* MYSQL14\_14	Mysql v14.14 (MYSQL)
* SQLITE3\_3\_8\_2	sqlite3 v3.8.2 (SQLITE)

Disclosure.  Although these are valid drivers I use Postgres.  I only created the other drivers as
a proof of concept to make sure that this would work for other database platforms.
I don't particularly care about those other platforms so their implementation / testing may
lag behind. I will try to keep them working :-)

valid topic_root would be the registration root.  As an example we can use 'com.db'.
what this does is set up the rpc with a prefix of com.db, and calls named:
connect, disconnect, query, operation, watch for the database engine. A complete example:

Demonstration mode (note, your -d (dsn) argument will certainly be different, except maybe for SQLITE):
```sh
sqlbridge -v -e PG -t 'com.db' -d 'dbname=autobahn host=192.168.200.230 user=autouser'
or
sqlbridge -e MYSQL -t 'com.db' -d 'db=autobahn user=root'
or
sqlbridge -e SQLITE -t 'com.db' -d 'database=/tmp/ab'
```

For each of the aforementioned sqlbridge examples we have set up com.db.CALL rpc entry points:

* com.db.query      run a database query (results are expected, for example 'select ...')
* com.db.operation  run a database query (no results expected, for example 'insert into ...')
* com.db.watch      postgres has a LISTEN operator.  watch lets us specify what to listen for, and what to call when an event is triggered. The other drivers stub this out as a no op.

There are two other rpcs created as well, but, they are not needed in this context (because we specify the database we are connecting to on the sqlbridge command line). They are:
* com.db.connect    connect to a different db
* com.db.disconnect disconnect from a db

Note: I am reserving the namespace from the declared topic_base. I will be adding other entry points,
so don't use, for example, com.db.mystuff if you plan on using sqlbridge.

## sqlcmd

Simple command line execution of sqlbridge topics

```
usage: sqlcmd [-h] [-w WSOCKET] [-r REALM] [-v] [-u USER] [-s PASSWORD]
              [-t TOPIC_BASE] [-c DB_CALL] [-q DB_QUERY] [-a DB_ARGS]

sql bridge for Autobahn

optional arguments:
  -h, --help            show this help message and exit
  -w WSOCKET, --websocket WSOCKET
                        web socket definition, default is:
                        ws://127.0.0.1:8080/ws
  -r REALM, --realm REALM
                        connect to websocket using realm, default is: realm1
  -v, --verbose         Verbose logging for debugging
  -u USER, --user USER  connect to websocket as user, default is: client
  -s PASSWORD, --secret PASSWORD
                        users "secret" password
  -t TOPIC_BASE, --topic TOPIC_BASE
                        your query will be executed against this topic base,
                        the default: com.db
  -c DB_CALL, --call DB_CALL
                        this is concatenated with topic_base after prepending
                        a dot, default : query
  -q DB_QUERY, --query DB_QUERY
                        this is the first argument to db_call, if db_call is
                        operation or query then this is the sql query to run.
                        If the operation is watch then this is the LISTEN to
                        watch : select 1
  -a DB_ARGS, --args DB_ARGS
                        if your query requires arguments they can be specified
                        in json format here, default is a blank dictionary :
                        {}
```

Sqlcmd is only meant as an example of how you run queries.  It is expected that
someone using the sqlbridge would put queries directly in their components.

### Generic Postgres examples

* select all tuples from a table
```sh
sqlcmd -t com.db -c query -q "select * from login"
[
    {
        "modified_timestamp": "2014-09-29 10:25:52.38656-05", 
        "modified_by_user": "2", 
        "id": "3", 
        "tzname": "America/Chicago", 
        "login": "db", 
        "password": "dbsecret", 
        "fullname": "db access"
    }, 
    {
        "modified_timestamp": "2014-09-29 10:25:52.38656-05", 
        "modified_by_user": "2", 
        "id": "10", 
        "tzname": "America/Chicago", 
        "login": "greg", 
        "password": "123test", 
        "fullname": "Greg Fausak"
    }
]
```
* update a tuple (note the -c operation because no results are expected)
```sh
sqlcmd -t com.db -c operation -q "update login set tzname = 'America/New_York' where id = 3"
```
* update a tuple (a better way)
```sh
sqlcmd -t com.db -c operation -q "update login set tzname = %(tzname)s where id = %(id)s" -a '{"tzname":"America/New_York","id":3}'
```
* update a tuple (an even better way) (note the -c query, and the returning \*)
```sh
sqlcmd -t com.db -c query -q "update login set tzname = %(tzname)s where id = %(id)s returning *" -a '{"tzname":"America/New_York","id":3}'
[
    {
        "modified_timestamp": "2014-11-06 12:49:23.720764-06", 
        "modified_by_user": "0", 
        "id": "3", 
        "tzname": "America/New_York", 
        "login": "db", 
        "password": "dbsecret", 
        "fullname": "db access"
    }
]
```
* watch for changes. Easy example.
```sh
sqlcmd -t com.db -c watch -q "testme"
```
Then, on another sqlcmd client connected to the same Autobahn router and realm:
```sh
sqlcmd -c operation -q "notify testme, 'this is a test'"
```
Back at the original watch command, we see:
```sh
watch: this is a test
```
* watch for changes. (a use case).  This example is going to be a little contrived.
Lets say you have a login table in your database (like I do).
And lets further say you have a trigger on that table that will NOTIFY LOGINCHANGE everytime a tuple
is inserted, updated or deleted from that table. How to do all that is beyond the scope of
this example. So, with my sqlcmd I can 'watch' the LOGINCHANGE notification and subscribe to
changes to it.  Like this:
```sh
sqlcmd -t com.db -c watch -q "LOGINCHANGE"
```
When I run that command the linux prompt does not immediately return, it just sits there.  Then, in another window, I run that
SQL update command setting the tzname to America/New_York. Then, back in this example I see:
```sh
watch:
[
    {
        "table": "login",
        "op": "update",
        "modified_timestamp": "2014-11-06 12:49:23.720764-06", 
        "modified_by_user": "0", 
        "id": "3", 
        "tzname": "America/New_York", 
        "login": "db", 
        "password": "dbsecret", 
        "fullname": "db access"
    }
]
```
Note that the payloads, and notify are completely under database control.  This becomes much more important
for session and authorization management.  The main idea here is that clients can communicate through database
notifications.  It doesn't make much sense to use the sqlcmd example script to watch for changes, but, you can
see how you might use it in an application.
