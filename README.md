# sqlbridge - Autobahn Database Service

SQL Bridge for Autobahn

## Summary

A simple database access component for Autobahn. This component builds bridges to database backends making
them accessible to Autobahn via topics.  The component can be used in its raw form to build custom
Autobahn deployments, or, the convenience scripts that haver been included can be used to
connect an sqlbridge to an already operating Autobahn router.  There are two test scripts included in
this distrubution, sqlbridge and sqlcmd. Brief documentation for each follows. The service
concept here is (in beautiful ascii art):

```
+--------+      +----------+      +-----------+      +---------+
| sqlcmd |<---->| Autobahn |<---->| sqlbridge |<---->| your db |
| client |      | Router   |      |  client   |      | server  |
+--------+      +----------+      +-----------+      +---------+
```

Before sqlcmd (or any client wanting to access the database) can run, first you need:
* A database (postgres, mysql, sqlite).  Installation and feeding beyond the scope
of this documentation.  One thing to note, the database need not be installed
on the sqlbridge client, as long as the sqlbridge client can reach it
via whatever connection mechanism the db server supports.
* An Autobahn router to connect to.  This can be any router that allows either unchallenged
connectivity, or, wampcra connectivity.
* Once the above two are satisfied, then sqlbridge can be fired up, connecting the Autobahn
router to the db server.
* Finally, once the above three are done, then sqlcmd (or any client) can query
the db server via the sqlbridge.
So without further ado...

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

valid topic_root would be the registration root.  As an example we can use 'com.db'.
what this does is set up the rpc with a prefix of com.db, and calls named:
connect, disconnect, query, operation, watch for the database engine. A complete example:

```sh
sqlbridge -v -e PG -t 'com.db' -d 'dbname=autobahn host=192.168.200.230 user=autouser'
or
sqlbridge -e MYSQL -t 'com.db' -d 'database=autobahn user=root'
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
* update a tuple
```sh
sqlcmd -t com.db -c operation -q "update login set tzname = 'America/New_York' where id = 3"
```
